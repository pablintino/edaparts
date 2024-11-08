"""Initial migration

Revision ID: 4cf347d8ae68
Revises: 
Create Date: 2024-11-06 20:26:10.695780

"""

import pathlib
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "4cf347d8ae68"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.create_table(
        "footprint_ref",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(length=400), nullable=False),
        sa.Column("reference", sa.String(length=150), nullable=False),
        sa.Column("alias", sa.String(length=150), nullable=True),
        sa.Column("description", sa.String(length=300), nullable=True),
        sa.Column(
            "storage_status",
            sa.Enum(
                "NOT_STORED",
                "STORING",
                "STORED",
                "STORAGE_FAILED",
                "DELETING",
                name="storagestatus",
            ),
            nullable=False,
        ),
        sa.Column("storage_error", sa.String(length=1024), nullable=True),
        sa.Column(
            "cad_type", sa.Enum("ALTIUM", "KICAD", name="cadtype"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "inventory_category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=300), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["inventory_category.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "inventory_location",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=100), nullable=True),
        sa.Column("dici", sa.String(length=70), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        op.f("ix_inventory_location_dici"), "inventory_location", ["dici"], unique=False
    )
    op.create_table(
        "library_ref",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(length=400), nullable=False),
        sa.Column("reference", sa.String(length=150), nullable=False),
        sa.Column("alias", sa.String(length=150), nullable=True),
        sa.Column("description", sa.String(length=300), nullable=True),
        sa.Column(
            "storage_status",
            sa.Enum(
                "NOT_STORED",
                "STORING",
                "STORED",
                "STORAGE_FAILED",
                "DELETING",
                name="storagestatus",
            ),
            nullable=False,
        ),
        sa.Column("storage_error", sa.String(length=1024), nullable=True),
        sa.Column(
            "cad_type", sa.Enum("ALTIUM", "KICAD", name="cadtype"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "component",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("mpn", sa.String(length=100), nullable=False),
        sa.Column("manufacturer", sa.String(length=100), nullable=False),
        sa.Column(
            "created_on", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column(
            "updated_on", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column("value", sa.String(length=100), nullable=True),
        sa.Column("package", sa.String(length=100), nullable=True),
        sa.Column("description", sa.String(length=200), nullable=True),
        sa.Column("comment_altium", sa.String(length=100), nullable=True),
        sa.Column("comment_kicad", sa.String(length=100), nullable=True),
        sa.Column("is_through_hole", sa.Boolean(), nullable=True),
        sa.Column("operating_temperature_min", sa.String(length=30), nullable=True),
        sa.Column("operating_temperature_max", sa.String(length=30), nullable=True),
        sa.Column("library_ref_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["library_ref_id"],
            ["library_ref.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mpn", "manufacturer", name="_mpn_manufacturer_uc"),
    )
    op.create_index(
        op.f("ix_component_manufacturer"), "component", ["manufacturer"], unique=False
    )
    op.create_index(op.f("ix_component_mpn"), "component", ["mpn"], unique=False)
    op.create_table(
        "capacitor_ceramic",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tolerance", sa.String(length=30), nullable=True),
        sa.Column("voltage", sa.String(length=30), nullable=True),
        sa.Column("composition", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "capacitor_electrolytic",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tolerance", sa.String(length=30), nullable=True),
        sa.Column("voltage", sa.String(length=30), nullable=True),
        sa.Column("material", sa.String(length=30), nullable=True),
        sa.Column("polarised", sa.Boolean(), nullable=True),
        sa.Column("esr", sa.String(length=30), nullable=True),
        sa.Column("lifetime_temperature", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "capacitor_tantalum",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tolerance", sa.String(length=30), nullable=True),
        sa.Column("voltage", sa.String(length=30), nullable=True),
        sa.Column("lifetime_temperature", sa.String(length=30), nullable=True),
        sa.Column("esr", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "component_footprint_asc",
        sa.Column("component_id", sa.Integer(), nullable=False),
        sa.Column("footprint_ref_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["component_id"],
            ["component.id"],
        ),
        sa.ForeignKeyConstraint(
            ["footprint_ref_id"],
            ["footprint_ref.id"],
        ),
    )
    op.create_table(
        "connector_pcb",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("orientation", sa.String(length=50), nullable=True),
        sa.Column("pitch", sa.String(length=30), nullable=True),
        sa.Column("voltage_rating", sa.String(length=30), nullable=True),
        sa.Column("current_rating", sa.String(length=30), nullable=True),
        sa.Column("number_of_rows", sa.String(length=30), nullable=True),
        sa.Column("number_of_contacts", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "crystal_oscillator",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("load_capacitance", sa.String(length=30), nullable=True),
        sa.Column("frequency", sa.String(length=30), nullable=True),
        sa.Column("frequency_tolerance", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "diode_rectifier",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("forward_voltage", sa.String(length=30), nullable=True),
        sa.Column("reverse_current_leakage", sa.String(length=30), nullable=True),
        sa.Column("max_forward_average_current", sa.String(length=30), nullable=True),
        sa.Column("max_reverse_vrrm", sa.String(length=30), nullable=True),
        sa.Column("diode_type", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "diode_tvs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("voltage_reverse_standoff", sa.String(length=30), nullable=True),
        sa.Column("voltage_breakdown_min", sa.String(length=30), nullable=True),
        sa.Column("voltage_clamping_max", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "diode_zener",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tolerance", sa.String(length=30), nullable=True),
        sa.Column("power_max", sa.String(length=30), nullable=True),
        sa.Column("voltage_forward", sa.String(length=30), nullable=True),
        sa.Column("voltage_zener", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "discrete_logic",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("logic_family", sa.String(length=30), nullable=True),
        sa.Column("logic_type", sa.String(length=30), nullable=True),
        sa.Column("number_of_bits", sa.String(length=30), nullable=True),
        sa.Column("propagation_delay", sa.String(length=30), nullable=True),
        sa.Column("supply_voltage_max", sa.String(length=30), nullable=True),
        sa.Column("supply_voltage_min", sa.String(length=30), nullable=True),
        sa.Column("logic_function", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ferrite_bead",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("number_of_lines", sa.String(length=30), nullable=True),
        sa.Column("dc_resistance", sa.String(length=30), nullable=True),
        sa.Column("impedance_freq", sa.String(length=30), nullable=True),
        sa.Column("current_rating", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "fuse_pptc",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("current_hold", sa.String(length=30), nullable=True),
        sa.Column("current_trip", sa.String(length=30), nullable=True),
        sa.Column("voltage_rating", sa.String(length=30), nullable=True),
        sa.Column("resistance_maximum", sa.String(length=30), nullable=True),
        sa.Column("resistance_minimum", sa.String(length=30), nullable=True),
        sa.Column("power_rating", sa.String(length=30), nullable=True),
        sa.Column("current_rating", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "inductor_choke",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("number_of_lines", sa.String(length=30), nullable=True),
        sa.Column("dc_resistance", sa.String(length=30), nullable=True),
        sa.Column("impedance_freq", sa.String(length=30), nullable=True),
        sa.Column("current_rating", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "inventory_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mpn", sa.String(length=100), nullable=False),
        sa.Column("manufacturer", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=100), nullable=True),
        sa.Column("last_buy_price", sa.Float(), nullable=True),
        sa.Column("dici", sa.String(length=70), nullable=False),
        sa.Column("component_id", sa.Integer(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["inventory_category.id"],
        ),
        sa.ForeignKeyConstraint(
            ["component_id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mpn", "manufacturer", name="_mpn_manufacturer_item_uc"),
    )
    op.create_index(
        op.f("ix_inventory_item_dici"), "inventory_item", ["dici"], unique=False
    )
    op.create_index(
        op.f("ix_inventory_item_manufacturer"),
        "inventory_item",
        ["manufacturer"],
        unique=False,
    )
    op.create_index(
        op.f("ix_inventory_item_mpn"), "inventory_item", ["mpn"], unique=False
    )
    op.create_table(
        "led_indicator",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("forward_voltage", sa.String(length=30), nullable=True),
        sa.Column("color", sa.String(length=30), nullable=True),
        sa.Column("lens_style", sa.String(length=50), nullable=True),
        sa.Column("lens_transparency", sa.String(length=30), nullable=True),
        sa.Column("dominant_wavelength", sa.String(length=30), nullable=True),
        sa.Column("test_current", sa.String(length=30), nullable=True),
        sa.Column("lens_size", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "memory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("technology", sa.String(length=50), nullable=True),
        sa.Column("memory_type", sa.String(length=50), nullable=True),
        sa.Column("size", sa.String(length=30), nullable=True),
        sa.Column("interface", sa.String(length=50), nullable=True),
        sa.Column("clock_frequency", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "microcontroller",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("core", sa.String(length=50), nullable=True),
        sa.Column("core_size", sa.String(length=30), nullable=True),
        sa.Column("speed", sa.String(length=30), nullable=True),
        sa.Column("flash_size", sa.String(length=30), nullable=True),
        sa.Column("ram_size", sa.String(length=30), nullable=True),
        sa.Column("peripherals", sa.String(length=250), nullable=True),
        sa.Column("connectivity", sa.String(length=250), nullable=True),
        sa.Column("voltage_supply", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "opamp",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("gain_bandwith", sa.String(length=30), nullable=True),
        sa.Column("output_type", sa.String(length=50), nullable=True),
        sa.Column("input_type", sa.String(length=50), nullable=True),
        sa.Column("amplifier_type", sa.String(length=50), nullable=True),
        sa.Column("slew_rate", sa.String(length=30), nullable=True),
        sa.Column("voltage_supplies", sa.String(length=30), nullable=True),
        sa.Column("voltage_input_offset", sa.String(length=30), nullable=True),
        sa.Column("current_output", sa.String(length=30), nullable=True),
        sa.Column("number_of_channels", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "optocoupler_digital",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("voltage_isolation", sa.String(length=30), nullable=True),
        sa.Column("voltage_saturation_max", sa.String(length=30), nullable=True),
        sa.Column("current_transfer_ratio_max", sa.String(length=30), nullable=True),
        sa.Column("current_transfer_ratio_min", sa.String(length=30), nullable=True),
        sa.Column("voltage_forward_typical", sa.String(length=30), nullable=True),
        sa.Column("voltage_output_max", sa.String(length=30), nullable=True),
        sa.Column("number_of_channels", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "optocoupler_linear",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("voltage_isolation", sa.String(length=30), nullable=True),
        sa.Column("transfer_gain", sa.String(length=30), nullable=True),
        sa.Column("input_forward_voltage", sa.String(length=30), nullable=True),
        sa.Column("servo_gain", sa.String(length=30), nullable=True),
        sa.Column("forward_gain", sa.String(length=30), nullable=True),
        sa.Column("non_linearity", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "oscillator_oscillator",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("base_resonator", sa.String(length=30), nullable=True),
        sa.Column("current_supply_max", sa.String(length=30), nullable=True),
        sa.Column("frequency", sa.String(length=30), nullable=True),
        sa.Column("frequency_stability", sa.String(length=30), nullable=True),
        sa.Column("voltage_supply", sa.String(length=30), nullable=True),
        sa.Column("output_type", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "potentiometer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("power_max", sa.String(length=30), nullable=True),
        sa.Column("tolerance", sa.String(length=30), nullable=True),
        sa.Column("resistance_min", sa.String(length=30), nullable=True),
        sa.Column("resistance_max", sa.String(length=30), nullable=True),
        sa.Column("number_of_turns", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "power_inductor",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tolerance", sa.String(length=30), nullable=True),
        sa.Column("resistance_dcr", sa.String(length=30), nullable=True),
        sa.Column("inductance_freq_test", sa.String(length=30), nullable=True),
        sa.Column("current_rating", sa.String(length=30), nullable=True),
        sa.Column("current_saturation", sa.String(length=30), nullable=True),
        sa.Column("core_material", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "resistor",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("power_max", sa.String(length=30), nullable=True),
        sa.Column("tolerance", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "switch_push_button",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("function", sa.String(length=50), nullable=True),
        sa.Column("dc_voltage_rating", sa.String(length=30), nullable=True),
        sa.Column("ac_voltage_rating", sa.String(length=30), nullable=True),
        sa.Column("current_rating", sa.String(length=30), nullable=True),
        sa.Column("circuit_type", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "switch_switch",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("voltage_rating", sa.String(length=30), nullable=True),
        sa.Column("current_rating", sa.String(length=30), nullable=True),
        sa.Column("number_of_positions", sa.String(length=30), nullable=True),
        sa.Column("circuit_type", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "transceiver",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("duplex", sa.String(length=30), nullable=True),
        sa.Column("data_rate", sa.String(length=30), nullable=True),
        sa.Column("protocol", sa.String(length=30), nullable=True),
        sa.Column("voltage_supply", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "transducer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("input_magnitude", sa.String(length=50), nullable=True),
        sa.Column("output_type", sa.String(length=50), nullable=True),
        sa.Column("proportional_gain", sa.String(length=50), nullable=True),
        sa.Column("supply_voltage", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "transformer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("number_of_windings", sa.String(length=30), nullable=True),
        sa.Column("primary_dc_resistance", sa.String(length=30), nullable=True),
        sa.Column("secondary_dc_resistance", sa.String(length=30), nullable=True),
        sa.Column("tertiary_dc_resistance", sa.String(length=30), nullable=True),
        sa.Column("leakage_inductance", sa.String(length=30), nullable=True),
        sa.Column("primary_inductance", sa.String(length=30), nullable=True),
        sa.Column("secondary_current_rating", sa.String(length=30), nullable=True),
        sa.Column("tertiary_current_rating", sa.String(length=30), nullable=True),
        sa.Column("primary_voltage_rating", sa.String(length=30), nullable=True),
        sa.Column("secondary_voltage_rating", sa.String(length=30), nullable=True),
        sa.Column("tertiary_voltage_rating", sa.String(length=30), nullable=True),
        sa.Column("nps_turns_ratio", sa.String(length=30), nullable=True),
        sa.Column("npt_turns_ratio", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "transistor_array_mosfet",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("number_of_channels", sa.String(length=30), nullable=True),
        sa.Column("rds_on", sa.String(length=30), nullable=True),
        sa.Column("vgs_max", sa.String(length=30), nullable=True),
        sa.Column("vgs_th", sa.String(length=30), nullable=True),
        sa.Column("vds_max", sa.String(length=30), nullable=True),
        sa.Column("ids_max", sa.String(length=30), nullable=True),
        sa.Column("current_total_max", sa.String(length=30), nullable=True),
        sa.Column("power_max", sa.String(length=30), nullable=True),
        sa.Column("channel_type", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "transistor_bjt",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vce_sat_max", sa.String(length=30), nullable=True),
        sa.Column("hfe", sa.String(length=30), nullable=True),
        sa.Column("vce_max", sa.String(length=30), nullable=True),
        sa.Column("ic_max", sa.String(length=50), nullable=True),
        sa.Column("power_max", sa.String(length=50), nullable=True),
        sa.Column("bjt_type", sa.String(length=10), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "transistor_mosfet",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rds_on", sa.String(length=30), nullable=True),
        sa.Column("vgs_max", sa.String(length=30), nullable=True),
        sa.Column("vgs_th", sa.String(length=30), nullable=True),
        sa.Column("vds_max", sa.String(length=30), nullable=True),
        sa.Column("ids_max", sa.String(length=30), nullable=True),
        sa.Column("power_max", sa.String(length=30), nullable=True),
        sa.Column("channel_type", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "triac",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("power_max", sa.String(length=30), nullable=True),
        sa.Column("vdrm", sa.String(length=30), nullable=True),
        sa.Column("current_rating", sa.String(length=30), nullable=True),
        sa.Column("dl_dt", sa.String(length=30), nullable=True),
        sa.Column("trigger_current", sa.String(length=30), nullable=True),
        sa.Column("latching_current", sa.String(length=30), nullable=True),
        sa.Column("holding_current", sa.String(length=30), nullable=True),
        sa.Column("gate_trigger_voltage", sa.String(length=30), nullable=True),
        sa.Column("emitter_forward_current", sa.String(length=30), nullable=True),
        sa.Column("emitter_forward_voltage", sa.String(length=30), nullable=True),
        sa.Column("triac_type", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "voltage_regulator_dcdc",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("voltage_input_min", sa.String(length=30), nullable=True),
        sa.Column("voltage_output_min_fixed", sa.String(length=30), nullable=True),
        sa.Column("voltage_output_max", sa.String(length=30), nullable=True),
        sa.Column("current_output", sa.String(length=30), nullable=True),
        sa.Column("frequency_switching", sa.String(length=30), nullable=True),
        sa.Column("topology", sa.String(length=50), nullable=True),
        sa.Column("output_type", sa.String(length=50), nullable=True),
        sa.Column("number_of_outputs", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "voltage_regulator_linear",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("gain_bandwith", sa.String(length=50), nullable=True),
        sa.Column("output_type", sa.String(length=50), nullable=True),
        sa.Column("voltage_output_min_fixed", sa.String(length=30), nullable=True),
        sa.Column("voltage_output_max", sa.String(length=30), nullable=True),
        sa.Column("voltage_dropout_max", sa.String(length=30), nullable=True),
        sa.Column("current_supply_max", sa.String(length=30), nullable=True),
        sa.Column("current_output", sa.String(length=30), nullable=True),
        sa.Column("pssr", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["component.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "inventory_item_location_stock",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actual_stock", sa.Float(), nullable=False),
        sa.Column("stock_min_level", sa.Float(), nullable=True),
        sa.Column("stock_notify_min_level", sa.Float(), nullable=True),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["inventory_item.id"],
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["inventory_location.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "inventory_item_property",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("property_name", sa.String(length=100), nullable=True),
        sa.Column("property_s_value", sa.String(length=100), nullable=True),
        sa.Column("property_i_value", sa.Integer(), nullable=True),
        sa.Column("property_f_value", sa.Float(), nullable=True),
        sa.Column("item_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["inventory_item.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("item_id", "property_name", name="_item_prop_uc"),
    )
    op.create_index(
        op.f("ix_inventory_item_property_property_name"),
        "inventory_item_property",
        ["property_name"],
        unique=False,
    )
    op.create_table(
        "inventory_item_location_stock_movement",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("stock_change", sa.Float(), nullable=False),
        sa.Column("reason", sa.String(length=100), nullable=False),
        sa.Column(
            "created_on", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column("stock_item_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["stock_item_id"],
            ["inventory_item_location_stock.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Create the extension we use for the views
    op.execute("CREATE EXTENSION IF NOT EXISTS tablefunc")

    # Search for all the views creation SQL files
    create_views = [
        sql_file
        for sql_file in pathlib.Path(__file__)
        .parent.parent.joinpath("views", revision)
        .glob("Create*.sql")
    ]
    # Run the views creation scripts
    for view_file in create_views:
        with open(view_file, "r") as f:
            op.get_bind().execute(text(f.read()))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # Drop the views
    with open(
        pathlib.Path(__file__).parent.parent.joinpath("views", "DropViews.sql"), "r"
    ) as f:
        op.get_bind().execute(text(f.read()))
    # Drop the tablefunc extension we use for the views
    op.execute("DROP EXTENSION IF EXISTS tablefunc")

    op.drop_table("inventory_item_location_stock_movement")
    op.drop_index(
        op.f("ix_inventory_item_property_property_name"),
        table_name="inventory_item_property",
    )
    op.drop_table("inventory_item_property")
    op.drop_table("inventory_item_location_stock")
    op.drop_table("voltage_regulator_linear")
    op.drop_table("voltage_regulator_dcdc")
    op.drop_table("triac")
    op.drop_table("transistor_mosfet")
    op.drop_table("transistor_bjt")
    op.drop_table("transistor_array_mosfet")
    op.drop_table("transformer")
    op.drop_table("transducer")
    op.drop_table("transceiver")
    op.drop_table("switch_switch")
    op.drop_table("switch_push_button")
    op.drop_table("resistor")
    op.drop_table("power_inductor")
    op.drop_table("potentiometer")
    op.drop_table("oscillator_oscillator")
    op.drop_table("optocoupler_linear")
    op.drop_table("optocoupler_digital")
    op.drop_table("opamp")
    op.drop_table("microcontroller")
    op.drop_table("memory")
    op.drop_table("led_indicator")
    op.drop_index(op.f("ix_inventory_item_mpn"), table_name="inventory_item")
    op.drop_index(op.f("ix_inventory_item_manufacturer"), table_name="inventory_item")
    op.drop_index(op.f("ix_inventory_item_dici"), table_name="inventory_item")
    op.drop_table("inventory_item")
    op.drop_table("inductor_choke")
    op.drop_table("fuse_pptc")
    op.drop_table("ferrite_bead")
    op.drop_table("discrete_logic")
    op.drop_table("diode_zener")
    op.drop_table("diode_tvs")
    op.drop_table("diode_rectifier")
    op.drop_table("crystal_oscillator")
    op.drop_table("connector_pcb")
    op.drop_table("component_footprint_asc")
    op.drop_table("capacitor_tantalum")
    op.drop_table("capacitor_electrolytic")
    op.drop_table("capacitor_ceramic")
    op.drop_index(op.f("ix_component_mpn"), table_name="component")
    op.drop_index(op.f("ix_component_manufacturer"), table_name="component")
    op.drop_table("component")
    op.drop_table("library_ref")
    op.drop_index(op.f("ix_inventory_location_dici"), table_name="inventory_location")
    op.drop_table("inventory_location")
    op.drop_table("inventory_category")
    op.drop_table("footprint_ref")
    # ### end Alembic commands ###