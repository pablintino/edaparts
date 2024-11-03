from models.components.capacitor_ceramic_model import CapacitorCeramicModel
from models.components.resistor_model import ResistorModel
from models.inventory.inventory_item_model import InventoryItemModel
from models.inventory.inventory_item_property import InventoryItemPropertyModel
from services import search_service


def test_get_component_search_ok(db_session):
    model_cap1 = CapacitorCeramicModel(
        voltage="16 V",
        composition="X7R",
        tolerance="10%",
        description="MLCC Ceramic 1 uF 16 V 10% Capacitor",
        value="1 uF",
        package="0603 (1608 Metric)",
        comment="=Value",
        type="capacitor_ceramic",
        is_through_hole=False,
        mpn="0603YC105KAT2A_1C",
        manufacturer="AVX",
    )

    db_session.add(model_cap1)
    db_session.commit()

    item_cap1 = InventoryItemModel(
        mpn="mpn1",
        manufacturer="manufacturer1",
        name="name1",
        description="description1",
        last_buy_price=1.2,
        dici="dici1",
    )

    item_cap1.component_id = model_cap1.id
    item_cap1.component = model_cap1
    db_session.add(item_cap1)
    db_session.commit()

    item_cap1_prop1 = InventoryItemPropertyModel(
        property_name="prop_cap_1_1",
        property_s_value="test value 1",
        item_id=item_cap1.id,
    )

    item_cap1_prop2 = InventoryItemPropertyModel(
        property_name="prop_int", property_i_value=1, item_id=item_cap1.id
    )
    item_cap1_prop3 = InventoryItemPropertyModel(
        property_name="prop_float", property_f_value=1.1, item_id=item_cap1.id
    )

    db_session.add(item_cap1_prop1)
    db_session.add(item_cap1_prop2)
    db_session.add(item_cap1_prop3)
    db_session.commit()

    model_cap2 = CapacitorCeramicModel(
        voltage="16 V",
        composition="X7R",
        tolerance="10%",
        description="MLCC Ceramic 1 uF 16 V 10% Capacitor",
        value="1 uF",
        package="0603 (1608 Metric)",
        comment="=Value",
        type="capacitor_ceramic",
        is_through_hole=False,
        mpn="0603YC105KAT2A_2B",
        manufacturer="AVX",
    )

    db_session.add(model_cap2)
    db_session.commit()

    item_cap2 = InventoryItemModel(
        mpn="mpn2",
        manufacturer="manufacturer2",
        name="name2",
        description="description2",
        last_buy_price=2.1,
        dici="dici2",
    )

    item_cap2.component_id = model_cap2.id
    item_cap2.component = model_cap2
    db_session.add(item_cap2)
    db_session.commit()

    item_cap2_prop1 = InventoryItemPropertyModel(
        property_name="prop_cap_2_1",
        property_s_value="test value 2",
        item_id=item_cap2.id,
    )

    item_cap2_prop2 = InventoryItemPropertyModel(
        property_name="prop_int", property_i_value=2, item_id=item_cap2.id
    )
    item_cap2_prop3 = InventoryItemPropertyModel(
        property_name="prop_float", property_f_value=2.2, item_id=item_cap2.id
    )

    db_session.add(item_cap2_prop1)
    db_session.add(item_cap2_prop2)
    db_session.add(item_cap2_prop3)
    db_session.commit()

    model_res1 = ResistorModel(
        power_max="2 W",
        tolerance="20 %",
        description="Thin Film Resistor 392 Ohms 1%",
        value="392 Ohms",
        package="0603 (1608 Metric)",
        comment="=Value",
        type="resistor",
        is_through_hole=True,
        mpn="CRCW0603392RFKEACA",
        manufacturer="Vishay / Dale",
    )

    db_session.add(model_res1)
    db_session.commit()

    item_res1 = InventoryItemModel(
        mpn="mpn3",
        manufacturer="manufacturer3",
        name="name3",
        description="description3",
        last_buy_price=3.1,
        dici="dici3",
    )

    item_res1.component_id = model_res1.id
    item_res1.component = model_res1
    db_session.add(item_res1)
    db_session.commit()

    item_res1_prop1 = InventoryItemPropertyModel(
        property_name="prop_res_1_1",
        property_s_value="test value 3",
        item_id=item_res1.id,
    )

    item_res1_prop2 = InventoryItemPropertyModel(
        property_name="prop_int", property_i_value=3, item_id=item_res1.id
    )
    item_res1_prop3 = InventoryItemPropertyModel(
        property_name="prop_float", property_f_value=3.3, item_id=item_res1.id
    )

    db_session.add(item_res1_prop1)
    db_session.add(item_res1_prop2)
    db_session.add(item_res1_prop3)
    db_session.commit()

    result1 = search_service.search_items({"prop_prop_res_1_1_like": "%value 3"}, 1, 20)

    assert result1.total == 1
    assert result1.items[0].id == item_res1.id

    result2 = search_service.search_items({"prop_prop_float_min": "2.0"}, 1, 20)

    assert result2.total == 2
    assert next((x for x in result2.items if x.id == item_cap2.id), None)
    assert next((x for x in result2.items if x.id == item_res1.id), None)

    result3 = search_service.search_items({"comp_mpn_like": "0603%"}, 1, 20)

    assert result3.total == 2
    assert next((x for x in result3.items if x.id == item_cap2.id), None)
    assert next((x for x in result3.items if x.id == item_cap1.id), None)

    result4 = search_service.search_items({"comp_is_through_hole_eq": "True"}, 1, 20)

    assert result4.total == 1
    assert next((x for x in result4.items if x.id == item_res1.id), None)

    result5 = search_service.search_items({"comp_is_through_hole_noteq": "True"}, 1, 20)

    assert result5.total == 2
    assert next((x for x in result5.items if x.id == item_cap2.id), None)
    assert next((x for x in result5.items if x.id == item_cap1.id), None)

    result6 = search_service.search_items({"prop_prop_int_min": "2"}, 1, 20)
    assert result6.total == 1
    assert next((x for x in result6.items if x.id == item_res1.id), None)

    result7 = search_service.search_items({"prop_prop_int_mineq": "2"}, 1, 20)
    assert result7.total == 2
    assert next((x for x in result7.items if x.id == item_cap2.id), None)
    assert next((x for x in result7.items if x.id == item_res1.id), None)

    result8 = search_service.search_items({"prop_prop_int_max": "2"}, 1, 20)
    assert result8.total == 1
    assert next((x for x in result8.items if x.id == item_cap1.id), None)

    result9 = search_service.search_items({"prop_prop_int_maxeq": "2"}, 1, 20)
    assert result9.total == 2
    assert next((x for x in result9.items if x.id == item_cap2.id), None)
    assert next((x for x in result9.items if x.id == item_cap1.id), None)

    result10 = search_service.search_items(
        {"prop_prop_int_mineq": "2", "comp_type_eq": "resistor"}, 1, 20
    )
    assert result10.total == 1
    assert next((x for x in result10.items if x.id == item_res1.id), None)

    result11 = search_service.search_items(
        {"comp_power_max_like": "2%", "comp_type_eq": "resistor"}, 1, 20
    )
    assert result11.total == 1
    assert next((x for x in result11.items if x.id == item_res1.id), None)

    result12 = search_service.search_items({"item_last_buy_price_max": 2.0}, 1, 20)
    assert result12.total == 1
    assert next((x for x in result12.items if x.id == item_cap1.id), None)

    result13 = search_service.search_items({"item_last_buy_price_maxeq": 2.1}, 1, 20)
    assert result13.total == 2
    assert next((x for x in result13.items if x.id == item_cap1.id), None)
    assert next((x for x in result13.items if x.id == item_cap2.id), None)
