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


from datetime import datetime

import pytest

from models import LibraryReference, FootprintReference
from models.components.capacitor_ceramic_model import CapacitorCeramicModel
from models.components.component_model import ComponentModel
from models.components.resistor_model import ResistorModel
from services import component_service
from services.exceptions import InvalidComponentFieldsError, ResourceNotFoundApiError, RelationAlreadyExistsError, \
    ResourceAlreadyExistsApiError


def __get_dummy_resistor_component():
    return ResistorModel(
        power_max='2 W',
        tolerance="20 %",
        description="Thin Film Resistor 392 Ohms 1%",
        value="392 Ohms",
        package="0603 (1608 Metric)",
        comment="=Value",
        type="resistor",
        is_through_hole=False,
        mpn="CRCW0603392RFKEAC",
        manufacturer="Vishay / Dale"
    )


def __check_component_creation(model, result, db_session):
    assert db_session.query(ComponentModel.id).count() == 1
    exists_id = db_session.query(ComponentModel.id).filter_by(mpn=model.mpn,
                                                              manufacturer=model.manufacturer).scalar()
    assert exists_id >= 0
    assert result is not None
    assert result.id == exists_id


def test_resistor_creation_ok(db_session):
    model = __get_dummy_resistor_component()

    result = component_service.create_component(model)
    __check_component_creation(model, result, db_session)


def test_capacitor_ceramic_creation_ok(db_session):
    model = CapacitorCeramicModel(
        voltage="16 V",
        composition="X7R",
        tolerance="10%",
        description="MLCC Ceramic 1 uF 16 V 10% Capacitor",
        value="1 uF",
        package="0603 (1608 Metric)",
        comment="=Value",
        type="capacitor_ceramic",
        is_through_hole=False,
        mpn="0603YC105KAT2A",
        manufacturer="AVX"
    )

    result = component_service.create_component(model)
    __check_component_creation(model, result, db_session)


def test_create_already_created_component_ko(db_session):
    model = component_service.create_component(__get_dummy_resistor_component())

    with pytest.raises(Exception) as e_info:
        component_service.create_component(__get_dummy_resistor_component())

    assert e_info.type is ResourceAlreadyExistsApiError
    assert e_info.value.conflicting_id == model.id


def test_create_component_reserved_fields_1_ko(db_session):
    model = __get_dummy_resistor_component()
    model.id = 1
    model.created_on = datetime.now()
    model.updated_on = datetime.now()

    with pytest.raises(Exception) as e_info:
        component_service.create_component(model)

    assert e_info.type is InvalidComponentFieldsError
    assert e_info.value.reserved_fields is not None
    assert len(e_info.value.reserved_fields) == 3


def test_update_create_symbol_relation_ok(db_session):
    component_model = __get_dummy_resistor_component()
    symbol_ref = LibraryReference(storage_status="NOT_STORED", symbol_path="/tes/test", description="dummy ref")
    db_session.add(component_model)
    db_session.add(symbol_ref)
    db_session.commit()

    component_service.update_create_symbol_relation(component_model.id, symbol_ref.id)

    result = db_session.query(ComponentModel.id, ComponentModel.library_ref_id).filter_by(id=component_model.id).first()
    assert result.library_ref_id == symbol_ref.id


def test_update_create_symbol_relation_symbol_not_found_ko(db_session):
    component_model = __get_dummy_resistor_component()
    db_session.add(component_model)
    db_session.commit()

    with pytest.raises(Exception) as e_info:
        component_service.update_create_symbol_relation(component_model.id, 7777)
    assert e_info.type is ResourceNotFoundApiError
    assert e_info.value.missing_id == 7777


def test_update_create_symbol_relation_component_not_found_ko(db_session):
    symbol_ref = LibraryReference(storage_status="NOT_STORED", symbol_path="/tes/test", description="dummy ref")
    db_session.add(symbol_ref)
    db_session.commit()

    with pytest.raises(Exception) as e_info:
        component_service.update_create_symbol_relation(9999, symbol_ref.id)

    assert e_info.type is ResourceNotFoundApiError
    assert e_info.value.missing_id == 9999


def test_update_create_symbol_relation_unauthorized_update_ko(db_session):
    component_model = __get_dummy_resistor_component()
    symbol_ref = LibraryReference(storage_status="NOT_STORED", symbol_path="/tes/test", description="dummy ref")

    component_model.library_ref = symbol_ref
    db_session.add(component_model)
    db_session.add(symbol_ref)
    db_session.commit()

    with pytest.raises(Exception) as e_info:
        component_service.update_create_symbol_relation(component_model.id, symbol_ref.id)

    assert e_info.type is RelationAlreadyExistsError


def test_create_footprint_relation_ok(db_session):
    component_model = __get_dummy_resistor_component()
    footprint_references = [
        FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test1", description="dummy ref"),
        FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test2", description="dummy ref"),
    ]
    db_session.add(component_model)
    db_session.add(footprint_references[0])
    db_session.add(footprint_references[1])
    db_session.commit()

    component_service.create_footprints_relation(component_model.id, [ref.id for ref in footprint_references])
    db_component = ComponentModel.query.get(component_model.id)

    assert len(db_component.footprint_refs) == 2
    assert next((x for x in db_component.footprint_refs if x.footprint_path == "/test/test1"), None)
    assert next((x for x in db_component.footprint_refs if x.footprint_path == "/test/test2"), None)

    extra_footprint_references = [
        FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test3", description="dummy ref"),
        FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test4", description="dummy ref"),
        footprint_references[0]]

    db_session.add(extra_footprint_references[0])
    db_session.add(extra_footprint_references[1])
    db_session.add(extra_footprint_references[2])
    db_session.commit()

    component_service.create_footprints_relation(component_model.id, [ref.id for ref in extra_footprint_references])
    db_component = ComponentModel.query.get(component_model.id)

    assert len(db_component.footprint_refs) == 4
    assert next((x for x in db_component.footprint_refs if x.footprint_path == "/test/test1"), None)
    assert next((x for x in db_component.footprint_refs if x.footprint_path == "/test/test2"), None)
    assert next((x for x in db_component.footprint_refs if x.footprint_path == "/test/test3"), None)
    assert next((x for x in db_component.footprint_refs if x.footprint_path == "/test/test4"), None)


def test_create_footprint_relation_component_not_found_ko(db_session):
    footprint_references = [
        FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test1", description="dummy ref"),
        FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test2", description="dummy ref"),
    ]
    db_session.add(footprint_references[0])
    db_session.add(footprint_references[1])
    db_session.commit()

    with pytest.raises(Exception) as e_info:
        component_service.create_footprints_relation(9999, [ref.id for ref in footprint_references])

    assert e_info.type is ResourceNotFoundApiError
    assert e_info.value.missing_id == 9999


def test_create_footprint_relation_footprint_not_found_ko(db_session):
    component_model = __get_dummy_resistor_component()
    footprint_references = [
        FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test1", description="dummy ref"),
        FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test2", description="dummy ref"),
    ]
    db_session.add(component_model)
    db_session.add(footprint_references[0])
    db_session.add(footprint_references[1])
    db_session.commit()

    with pytest.raises(Exception) as e_info:
        component_service.create_footprints_relation(component_model.id,
                                                     [ref.id for ref in footprint_references] + [9999])

    db_component = ComponentModel.query.get(component_model.id)

    assert e_info.type is ResourceNotFoundApiError
    assert e_info.value.missing_id == 9999
    assert len(db_component.footprint_refs) == 0


def test_get_component_footprint_relations_ok(db_session):
    component_model = __get_dummy_resistor_component()
    footprint_references = [
        FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test1", description="dummy ref"),
        FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test2", description="dummy ref"),
    ]

    db_session.add(footprint_references[0])
    db_session.add(footprint_references[1])
    db_session.commit()

    component_model.footprint_refs.append(footprint_references[0])
    component_model.footprint_refs.append(footprint_references[1])
    db_session.add(component_model)
    db_session.commit()

    result = component_service.get_component_footprint_relations(component_model.id)
    assert len(result) == 2
    assert next((x for x in result if x == footprint_references[0].id), None)
    assert next((x for x in result if x == footprint_references[1].id), None)

    result_all = component_service.get_component_footprint_relations(component_model.id, complete_footprints=True)
    assert len(result_all) == 2
    assert next((x for x in result_all if x.footprint_path == "/test/test1"), None)
    assert next((x for x in result_all if x.footprint_path == "/test/test2"), None)


def test_get_component_symbol_relation_ok(db_session):
    component_model = __get_dummy_resistor_component()
    symbol_ref = LibraryReference(storage_status="NOT_STORED", symbol_path="/tes/test", description="dummy ref")

    component_model.library_ref = symbol_ref
    db_session.add(component_model)
    db_session.add(symbol_ref)
    db_session.commit()

    result = component_service.get_component_symbol_relation(component_model.id)
    assert result.symbol_path == symbol_ref.symbol_path


def test_get_component_symbol_relation_component_not_found_ko(db_session):
    with pytest.raises(Exception) as e_info:
        component_service.get_component_symbol_relation(9999)

    assert e_info.type is ResourceNotFoundApiError
    assert e_info.value.missing_id == 9999


def test_get_component_footprint_relations_component_not_found_ko(db_session):
    with pytest.raises(Exception) as e_info:
        component_service.get_component_footprint_relations(9999)

    assert e_info.type is ResourceNotFoundApiError
    assert e_info.value.missing_id == 9999


def test_get_component_ok(db_session):
    model = __get_dummy_resistor_component()
    db_session.add(model)
    db_session.commit()

    result = component_service.get_component(model.id)
    assert result.id == model.id


def test_get_component_component_not_found_ko(db_session):
    with pytest.raises(Exception) as e_info:
        component_service.get_component(9999)
    assert e_info.type is ResourceNotFoundApiError
    assert e_info.value.missing_id == 9999


def test_delete_component_ok(db_session):
    model = __get_dummy_resistor_component()
    db_session.add(model)
    db_session.commit()

    component_service.delete_component(model.id)

    assert ComponentModel.query.get(model.id) is None


def test_delete_component_symbol_relation_ok(db_session):
    component_model = __get_dummy_resistor_component()
    symbol_ref = LibraryReference(storage_status="NOT_STORED", symbol_path="/tes/test", description="dummy ref")

    component_model.library_ref = symbol_ref
    db_session.add(component_model)
    db_session.add(symbol_ref)
    db_session.commit()

    component_service.delete_component_symbol_relation(component_model.id)
    db_component = ComponentModel.query.get(component_model.id)

    assert db_component.library_ref_id is None
    assert db_component.library_ref is None


def test_delete_component_symbol_relation_no_component_ko(db_session):
    symbol_ref = LibraryReference(storage_status="NOT_STORED", symbol_path="/tes/test", description="dummy ref")
    db_session.add(symbol_ref)
    db_session.commit()

    with pytest.raises(Exception) as e_info:
        component_service.delete_component_symbol_relation(9999)
    assert e_info.type is ResourceNotFoundApiError
    assert e_info.value.missing_id == 9999


def test_delete_component_footprint_relations_ok(db_session):
    component_model = __get_dummy_resistor_component()
    footprint_references = [
        FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test1", description="dummy ref"),
        FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test2", description="dummy ref"),
        FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test3", description="dummy ref")
    ]

    db_session.add(footprint_references[0])
    db_session.add(footprint_references[1])
    db_session.add(footprint_references[2])
    db_session.commit()

    component_model.footprint_refs.append(footprint_references[0])
    component_model.footprint_refs.append(footprint_references[1])
    component_model.footprint_refs.append(footprint_references[2])
    db_session.add(component_model)
    db_session.commit()

    component_service.delete_component_footprint_relation(component_model.id, footprint_references[0].id)
    db_component = ComponentModel.query.get(component_model.id)
    assert len(db_component.footprint_refs) == 2
    assert next((x for x in db_component.footprint_refs if x.id == footprint_references[1].id), None)
    assert next((x for x in db_component.footprint_refs if x.id == footprint_references[2].id), None)
    component_service.delete_component_footprint_relation(component_model.id, footprint_references[1].id)
    component_service.delete_component_footprint_relation(component_model.id, footprint_references[2].id)
    db_component = ComponentModel.query.get(component_model.id)
    assert len(db_component.footprint_refs) == 0


def test_delete_component_footprint_relation_no_component_ko(db_session):
    footprint_reference = FootprintReference(storage_status="NOT_STORED", footprint_path="/test/test1",
                                             description="dummy ref")

    db_session.add(footprint_reference)
    db_session.commit()

    with pytest.raises(Exception) as e_info:
        component_service.delete_component_footprint_relation(9999, footprint_reference.id)
    assert e_info.type is ResourceNotFoundApiError
    assert e_info.value.missing_id == 9999


def test_update_component_ok(db_session):
    model = __get_dummy_resistor_component()
    db_session.add(model)
    db_session.commit()

    update_data = {
        "power_max": '5 W',
        "tolerance": "10 %"
    }

    result = component_service.update_component(model.id, update_data)
    assert result.id == model.id
    assert result.power_max == update_data['power_max']
    assert result.tolerance == update_data['tolerance']

    db_component = ComponentModel.query.get(model.id)
    assert db_component.id == model.id
    assert db_component.power_max == update_data['power_max']
    assert db_component.tolerance == update_data['tolerance']


def test_update_component_reserved_fields_ko(db_session):
    model = __get_dummy_resistor_component()
    db_session.add(model)
    db_session.commit()

    update_data = {
        "power_max": '5 W',
        "tolerance": "10 %",
        "created_on": datetime.now(),
        "updated_on": datetime.now(),
        "mpn": "test",
        "manufacturer": "test"
    }
    with pytest.raises(Exception) as e_info:
        component_service.update_component(model.id, update_data)
    assert e_info.value.reserved_fields is not None
    assert next((x for x in e_info.value.reserved_fields if x == "created_on"), None)
    assert next((x for x in e_info.value.reserved_fields if x == "updated_on"), None)
    assert next((x for x in e_info.value.reserved_fields if x == "mpn"), None)
    assert next((x for x in e_info.value.reserved_fields if x == "manufacturer"), None)
