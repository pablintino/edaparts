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


import pytest

from dtos import component_model_mapper
from models.components.resistor_model import ResistorModel
from services.exceptions import InvalidComponentFieldsError, InvalidComponentTypeError


def __assert_base_component(result, expected):
    assert expected.description == result.description
    assert expected.value == result.value
    assert expected.package == result.package
    assert expected.comment == result.comment
    assert expected.type == result.type
    assert expected.is_through_hole == result.is_through_hole
    assert expected.mpn == result.mpn
    assert expected.manufacturer == result.manufacturer


def __assert_base_raw_resistor(mapped):
    assert mapped["power_max"] == "100 mW"
    assert mapped["tolerance"] == "1%"
    assert mapped["description"] == "Thin Film Resistor 392 Ohms 1%"
    assert mapped["value"] == "392 Ohms"
    assert mapped["package"] == "0603 (1608 Metric)"
    assert mapped["comment"] == "=Value"
    assert mapped["operating_temperature_min"] == "-40 ºC"
    assert mapped["operating_temperature_max"] == "125 ºC"
    assert mapped["type"] == "resistor"
    assert mapped["is_through_hole"] == False
    assert mapped["mpn"] == "CRCW0603392RFKEAC"
    assert mapped["manufacturer"] == "Vishay / Dale"


def __get_generic_raw_resistor():
    return {
        "power_max": "100 mW",
        "tolerance": "1%",
        "description": "Thin Film Resistor 392 Ohms 1%",
        "value": "392 Ohms",
        "package": "0603 (1608 Metric)",
        "comment": "=Value",
        "operating_temperature_min": "-40 ºC",
        "operating_temperature_max": "125 ºC",
        "type": "resistor",
        "is_through_hole": False,
        "mpn": "CRCW0603392RFKEAC",
        "manufacturer": "Vishay / Dale",
    }


def test_map_raw_component_ok():
    raw = __get_generic_raw_resistor()

    mapped = component_model_mapper.map_validate_raw(raw, pk_provided=False)
    __assert_base_raw_resistor(mapped)


def test_map_raw_component_given_type_ok():
    raw = __get_generic_raw_resistor()
    raw.pop("type")
    mapped = component_model_mapper.map_validate_raw(
        raw, pk_provided=False, force_type="resistor"
    )
    assert "type" not in mapped
    mapped["type"] = "resistor"
    __assert_base_raw_resistor(mapped)


def test_map_raw_component_ignore_mandatory_ok():
    raw = __get_generic_raw_resistor()
    raw.pop("mpn")
    raw.pop("manufacturer")
    mapped = component_model_mapper.map_validate_raw(
        raw, pk_provided=False, ignore_mandatory=True
    )
    assert "mpn" not in mapped
    assert "manufacturer" not in mapped
    mapped["mpn"] = __get_generic_raw_resistor().get("mpn", None)
    mapped["manufacturer"] = __get_generic_raw_resistor().get("manufacturer", None)
    __assert_base_raw_resistor(mapped)


def test_map_resistor_ok():
    raw = __get_generic_raw_resistor()

    model = ResistorModel(
        power_max="2 W",
        tolerance="20 %",
        description="Thin Film Resistor 392 Ohms 1%",
        value="392 Ohms",
        package="0603 (1608 Metric)",
        comment="=Value",
        operating_temperature_min="-40 ºC",
        operating_temperature_max="125 ºC",
        type="resistor",
        is_through_hole=False,
        mpn="CRCW0603392RFKEAC",
        manufacturer="Vishay / Dale",
    )

    mapped = component_model_mapper.map_validate_raw_to_model(raw, pk_provided=False)
    __assert_base_component(mapped, model)


def test_map_model_to_raw_resistor_ok():
    model = ResistorModel(
        power_max="2 W",
        tolerance="20 %",
        description="Thin Film Resistor 392 Ohms 1%",
        value="392 Ohms",
        package="0603 (1608 Metric)",
        comment="=Value",
        operating_temperature_min="-40 ºC",
        operating_temperature_max="125 ºC",
        type="resistor",
        is_through_hole=False,
        mpn="CRCW0603392RFKEAC",
        manufacturer="Vishay / Dale",
    )

    raw = component_model_mapper.map_model_to_raw(model)
    assert model.power_max == raw["power_max"]
    assert model.tolerance == raw["tolerance"]
    assert model.description == raw["description"]
    assert model.value == raw["value"]
    assert model.package == raw["package"]
    assert model.comment == raw["comment"]
    assert model.type == raw["type"]
    assert model.is_through_hole == raw["is_through_hole"]
    assert model.mpn == raw["mpn"]
    assert model.manufacturer == raw["manufacturer"]
    assert model.operating_temperature_min == raw["operating_temperature_min"]
    assert model.operating_temperature_max == raw["operating_temperature_max"]


def test_map_component_not_expected_field_ko():
    raw = __get_generic_raw_resistor()
    raw["thisfieldshouldtbepresent"] = "wololo"

    with pytest.raises(Exception) as e_info:
        component_model_mapper.map_validate_raw(
            raw, pk_provided=False, ignore_mandatory=False
        )

    assert e_info.type is InvalidComponentFieldsError
    assert e_info.value.unrecognised_fields is not None
    assert len(e_info.value.unrecognised_fields) == 1
    assert e_info.value.unrecognised_fields[0] == "thisfieldshouldtbepresent"


def test_map_component_not_expected_type_ko():
    raw = __get_generic_raw_resistor()
    raw["type"] = "shouldnotexist"

    with pytest.raises(Exception) as e_info:
        component_model_mapper.map_validate_raw(
            raw, pk_provided=False, ignore_mandatory=False
        )

    assert e_info.type is InvalidComponentTypeError

    # Try map without type
    del raw["type"]
    with pytest.raises(Exception) as e_info:
        component_model_mapper.map_validate_raw(
            raw, pk_provided=False, ignore_mandatory=False
        )

    assert e_info.type is InvalidComponentTypeError


def test_map_component_not_expected_field_type_ko():
    raw = __get_generic_raw_resistor()
    raw["power_max"] = 1.0
    with pytest.raises(Exception) as e_info:
        component_model_mapper.map_validate_raw(
            raw, pk_provided=False, ignore_mandatory=False
        )

    assert e_info.type is InvalidComponentFieldsError
    assert e_info.value.unexpected_types is not None
    assert len(e_info.value.unexpected_types) == 1
    assert e_info.value.unexpected_types[0] == "power_max"


def test_map_component_no_mandatory_field_ko():
    raw = __get_generic_raw_resistor()
    del raw["mpn"]
    with pytest.raises(Exception) as e_info:
        component_model_mapper.map_validate_raw(
            raw, pk_provided=False, ignore_mandatory=False
        )

    assert e_info.type is InvalidComponentFieldsError
    assert e_info.value.mandatory_missing is not None
    assert len(e_info.value.mandatory_missing) == 1
    assert e_info.value.mandatory_missing[0] == "mpn"
