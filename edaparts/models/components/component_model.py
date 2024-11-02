#
# MIT License
#
# Copyright (c) 2024 Pablo Rodriguez Nava, @pablintino
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#


from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    UniqueConstraint,
    ForeignKey,
    Boolean,
    func,
)
from sqlalchemy.orm import relationship

from edaparts.models.inventory.inventory_identificable_item_model import (
    InventoryIdentificableItemModel,
)
from edaparts.models.libraries.join_tables import component_footprint_asc_table


class ComponentModel(InventoryIdentificableItemModel):
    __tablename__ = "component"
    __id_prefix__ = "COMP"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # This column tells the ORM the specific component child type
    type = Column(String(50))

    # General component properties
    mpn = Column(String(100), nullable=False, index=True)
    manufacturer = Column(String(100), nullable=False, index=True)
    created_on = Column(DateTime(), server_default=func.now())
    updated_on = Column(DateTime(), server_default=func.now(), onupdate=func.now())
    value = Column(String(100))
    package = Column(String(100))
    description = Column(String(200))
    comment_altium = Column(String(100), nullable=True)
    comment_kicad = Column(String(100), nullable=True)
    is_through_hole = Column(Boolean())
    operating_temperature_min = Column(String(30))
    operating_temperature_max = Column(String(30))

    # Relationships
    library_ref_id = Column(Integer, ForeignKey("library_ref.id"))
    library_ref = relationship(
        "LibraryReference", back_populates="library_components", lazy="select"
    )
    footprint_refs = relationship(
        "FootprintReference",
        secondary=component_footprint_asc_table,
        lazy="select",
        back_populates="components_f",
    )
    inventory_item = relationship(
        "InventoryItemModel", back_populates="component", uselist=False, lazy="select"
    )

    __mapper_args__ = {
        "polymorphic_identity": "component",
        "polymorphic_on": type,
        "with_polymorphic": "*",
    }

    # Set a constraint that enforces Part Number - Manufacturer uniqueness
    __table_args__ = (
        UniqueConstraint("mpn", "manufacturer", name="_mpn_manufacturer_uc"),
    )
