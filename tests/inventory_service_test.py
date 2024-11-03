import pytest
import random
import string

from models.components.capacitor_ceramic_model import CapacitorCeramicModel
from models.internal.internal_inventory_models import (
    MassStockMovement,
    SingleStockMovement,
)
from models.inventory.inventory_category_model import InventoryCategoryModel
from models.inventory.inventory_item_location_stock import (
    InventoryItemLocationStockModel,
)
from models.inventory.inventory_item_model import InventoryItemModel
from models.inventory.inventory_item_property import InventoryItemPropertyModel
from models.inventory.inventory_location import InventoryLocationModel
from services import inventory_service
from services.exceptions import (
    ResourceAlreadyExistsApiError,
    ResourceNotFoundApiError,
    InvalidMassStockUpdateError,
)


def __id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def __get_dummy_component(mpn=None, manufacturer=None):
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
        mpn="0603YC105KAT2A_1C" if not mpn else mpn,
        manufacturer="AVX" if not manufacturer else manufacturer,
    )
    return model_cap1


def __create_dummy_category(db_session, suffix):
    model = InventoryCategoryModel(
        name="category" + str(suffix), description="description" + str(suffix)
    )
    db_session.add(model)
    db_session.commit()
    return model


def __create_dummy_component_item(db_session, mpn=None, manufacturer=None):
    model = __get_dummy_component(mpn, manufacturer)
    db_session.add(model)
    db_session.commit()

    item_cap1 = InventoryItemModel(
        mpn=model.mpn,
        manufacturer=model.manufacturer,
        name=model.mpn,
        description=model.description,
        last_buy_price=1.2,
        dici=__id_generator(),
    )

    item_cap1.component_id = model.id
    item_cap1.component = model
    db_session.add(item_cap1)
    db_session.commit()

    return item_cap1


def __create_dummy_standalone_item(db_session, mpn, manufacturer):

    item_model = InventoryItemModel(
        mpn=mpn,
        manufacturer=manufacturer,
        name=mpn,
        description=mpn,
        last_buy_price=1.2,
        dici=__id_generator(),
    )

    db_session.add(item_model)
    db_session.commit()

    return item_model


def __get_create_item_location_and_stock(db_session, suffix):
    item_model = __create_dummy_component_item(
        db_session, mpn="test1" + str(suffix), manufacturer="test1" + str(suffix)
    )
    location_model = InventoryLocationModel(
        name="location" + str(suffix),
        description="description" + str(suffix),
        dici="dummydici" + str(suffix),
    )

    db_session.add(location_model)
    db_session.commit()
    return item_model, location_model


def __get_create_item_location_stock(db_session, item_id, location_id, quantity=0.0):
    item_stock_loc = InventoryItemLocationStockModel(
        location_id=location_id,
        item_id=item_id,
        actual_stock=quantity,
        stock_min_level=0.0,
        stock_notify_min_level=0.0,
    )

    db_session.add(item_stock_loc)
    db_session.commit()
    return item_stock_loc


def test_get_item_ok(db_session):
    item = __create_dummy_component_item(db_session)
    model = inventory_service.get_item(item.id)
    assert model.id == item.id


def test_create_item_for_component_ok(db_session):
    component = __get_dummy_component()
    db_session.add(component)
    db_session.commit()

    item = inventory_service.create_item_for_component(component, auto_commit=True)

    assert db_session.query(InventoryItemModel.id).count() == 1
    item_model = InventoryItemModel.query.get(item.id)
    assert item_model is not None
    assert item_model.dici is not None
    assert item_model.manufacturer == component.manufacturer
    assert item_model.mpn == component.mpn


def test_create_standalone_item_ok(db_session):
    model = InventoryItemModel(
        mpn="mnp_test",
        manufacturer="test manufacturer",
        name="test name",
        description="test description",
    )

    item = inventory_service.create_standalone_item(model)

    assert db_session.query(InventoryItemModel.id).count() == 1
    item_model = InventoryItemModel.query.get(item.id)
    assert item_model is not None
    assert item_model.dici is not None
    assert item_model.manufacturer == model.manufacturer
    assert item_model.mpn == model.mpn
    assert item_model.name == model.name
    assert item_model.description == model.description


def test_create_item_for_component_item_already_exists_ko(db_session):
    item = __create_dummy_component_item(db_session)
    assert item is not None

    component = __get_dummy_component()

    with pytest.raises(Exception) as e_info:
        inventory_service.create_item_for_component(component, auto_commit=True)

    assert e_info.type is ResourceAlreadyExistsApiError
    assert e_info.value.conflicting_id == item.id


def test_create_location_ok(db_session):
    location = inventory_service.create_location(
        "location_name", "location_description"
    )

    assert db_session.query(InventoryLocationModel.id).count() == 1
    location_model = InventoryLocationModel.query.get(location.id)
    assert location_model is not None
    assert location_model.name == location.name
    assert location_model.description == location.description


def test_add_property_to_item_ok(db_session):
    item = __create_dummy_component_item(db_session)
    assert item is not None

    item_property = InventoryItemPropertyModel(
        property_name="test_prop", property_s_value="test_value"
    )
    item_property = inventory_service.add_property_to_item(item.id, item_property)

    assert db_session.query(InventoryItemPropertyModel.id).count() == 1
    property_model = InventoryItemPropertyModel.query.get(item_property.id)
    assert property_model is not None
    assert property_model.property_name == item_property.property_name
    assert property_model.property_s_value == item_property.property_s_value


def test_update_item_property_ok(db_session):
    item = __create_dummy_component_item(db_session)
    assert item is not None

    item_property = InventoryItemPropertyModel(
        property_name="test_prop", property_s_value="test_value"
    )
    db_session.add(item_property)
    db_session.commit()

    inventory_service.update_item_property(item.id, item_property.id, 3)

    property_model = InventoryItemPropertyModel.query.get(item_property.id)
    assert property_model is not None
    assert property_model.property_name == item_property.property_name
    assert property_model.property_s_value is None
    assert property_model.property_i_value == 3
    assert property_model.property_f_value is None

    inventory_service.update_item_property(item.id, item_property.id, 3.2)

    property_model = InventoryItemPropertyModel.query.get(item_property.id)
    assert property_model is not None
    assert property_model.property_name == item_property.property_name
    assert property_model.property_s_value is None
    assert property_model.property_i_value is None
    assert property_model.property_f_value == 3.2


def test_get_item_properties_ok(db_session):
    item = __create_dummy_component_item(db_session, manufacturer="man1")
    item2 = __create_dummy_component_item(db_session, manufacturer="man2")
    assert item is not None
    assert item2 is not None

    item_property1 = InventoryItemPropertyModel(
        property_name="test_prop1", property_s_value="test_value", item_id=item.id
    )
    item_property2 = InventoryItemPropertyModel(
        property_name="test_prop2", property_s_value="test_value", item_id=item.id
    )
    item_property3 = InventoryItemPropertyModel(
        property_name="test_prop3", property_s_value="test_value", item_id=item2.id
    )
    db_session.add(item_property1)
    db_session.add(item_property2)
    db_session.add(item_property3)
    db_session.commit()

    props = inventory_service.get_item_properties(item.id)
    props2 = inventory_service.get_item_properties(item2.id)

    assert props is not None
    assert props2 is not None
    assert len(props) == 2
    assert len(props2) == 1
    assert next((x for x in props if x.id == item_property1.id), None)
    assert next((x for x in props if x.id == item_property2.id), None)
    assert next((x for x in props2 if x.id == item_property3.id), None)


def test_delete_item_property_ok(db_session):
    item = __create_dummy_component_item(db_session)
    assert item is not None

    item_property1 = InventoryItemPropertyModel(
        property_name="test_prop1", property_s_value="test_value", item_id=item.id
    )
    db_session.add(item_property1)
    db_session.commit()

    assert InventoryItemPropertyModel.query.get(item_property1.id) is not None

    inventory_service.delete_item_property(item_property1.id)
    assert InventoryItemPropertyModel.query.get(item_property1.id) is None


def test_create_category_ok(db_session):
    category = inventory_service.create_category(
        "category_name", "category_description"
    )

    assert db_session.query(InventoryCategoryModel.id).count() == 1
    category_model = InventoryCategoryModel.query.get(category.id)
    assert category_model is not None
    assert category_model.name == category.name
    assert category_model.description == category.description


def test_set_category_parent_ok(db_session):
    category_child = InventoryCategoryModel(name="child", description="test desc child")
    category_parent = InventoryCategoryModel(
        name="parent", description="test desc parent"
    )

    category_child_1 = InventoryCategoryModel(
        name="chield 1", description="test desc child 1"
    )
    category_child_2 = InventoryCategoryModel(
        name="chield 2", description="test desc child 2"
    )

    db_session.add(category_child)
    db_session.add(category_parent)
    db_session.add(category_child_1)
    db_session.add(category_child_2)
    db_session.commit()

    inventory_service.set_category_parent(category_child.id, category_parent.id)

    inventory_service.set_category_parent(category_child_1.id, category_child.id)
    inventory_service.set_category_parent(category_child_2.id, category_child.id)

    category_model = InventoryCategoryModel.query.get(category_child.id)

    assert category_model is not None
    assert category_model.parent_id == category_parent.id
    assert len(category_model.children) == 2
    assert next(
        (x for x in category_model.children if x.id == category_child_1.id), None
    )
    assert next(
        (x for x in category_model.children if x.id == category_child_2.id), None
    )


def test_remove_category_parent_ok(db_session):
    category_parent = InventoryCategoryModel(
        name="parent", description="test desc parent"
    )
    category_child_1 = InventoryCategoryModel(
        name="chield 1", description="test desc child 1"
    )
    category_child_2 = InventoryCategoryModel(
        name="chield 2", description="test desc child 2"
    )

    db_session.add(category_parent)
    db_session.add(category_child_1)
    db_session.add(category_child_2)
    db_session.commit()

    category_child_1.parent_id = category_parent.id
    category_child_2.parent_id = category_child_1.id

    db_session.add(category_child_1)
    db_session.add(category_child_2)
    db_session.commit()

    inventory_service.remove_category_parent(category_child_1.id)

    category_model_1 = InventoryCategoryModel.query.get(category_child_1.id)
    category_model_2 = InventoryCategoryModel.query.get(category_child_2.id)
    category_model_p = InventoryCategoryModel.query.get(category_parent.id)

    assert category_model_1 is not None
    assert category_model_2 is not None
    assert category_model_p is not None
    assert category_model_2.parent_id == category_model_1.id
    assert len(category_model_p.children) == 0
    assert len(category_model_1.children) == 1
    assert next(
        (x for x in category_model_1.children if x.id == category_model_2.id), None
    )


def test_update_category_ok(db_session):
    category = InventoryCategoryModel(name="test name", description="test description")
    db_session.add(category)
    db_session.commit()

    inventory_service.update_category(category.id, "edited name", "edited description")

    category_model = InventoryCategoryModel.query.get(category.id)

    assert category_model is not None
    assert category_model.name == "edited name"
    assert category_model.description == "edited description"


def test_set_item_category_ok(db_session):
    item_model = __create_dummy_component_item(db_session)
    category_model = InventoryCategoryModel(
        name="test name", description="test description"
    )
    db_session.add(category_model)
    db_session.commit()

    inventory_service.set_item_category(item_model.id, category_model.id)
    item_db_model = InventoryItemModel.query.get(item_model.id)
    assert item_db_model is not None
    assert item_model.category_id == category_model.id


def test_stock_mass_update_ok(db_session):
    item_model_1, location_model_1 = __get_create_item_location_and_stock(db_session, 1)
    item_model_2, location_model_2 = __get_create_item_location_and_stock(db_session, 2)
    item_stock_loc_1 = __get_create_item_location_stock(
        db_session, item_model_1.id, location_model_1.id
    )
    item_stock_loc_2 = __get_create_item_location_stock(
        db_session, item_model_2.id, location_model_2.id
    )

    movement = MassStockMovement(
        reason="test move",
        comment="test comment",
        movements=[
            SingleStockMovement(
                item_id=item_model_1.id, location_id=location_model_1.id, quantity=3
            ),
            SingleStockMovement(
                item_id=item_model_2.id, location_id=location_model_2.id, quantity=1
            ),
        ],
    )

    inventory_service.stock_mass_update(movement)
    stock_item_location_1 = InventoryItemLocationStockModel.query.get(
        item_stock_loc_1.id
    )
    stock_item_location_2 = InventoryItemLocationStockModel.query.get(
        item_stock_loc_2.id
    )
    assert stock_item_location_1 is not None
    assert stock_item_location_2 is not None
    assert stock_item_location_1.actual_stock == 3
    assert stock_item_location_2.actual_stock == 1

    movement = MassStockMovement(
        reason="test move",
        comment="test comment",
        movements=[
            SingleStockMovement(
                item_id=item_model_1.id, location_id=location_model_1.id, quantity=-2
            ),
            SingleStockMovement(
                item_id=item_model_2.id, location_id=location_model_2.id, quantity=-1
            ),
        ],
    )

    inventory_service.stock_mass_update(movement)
    stock_item_location_1 = InventoryItemLocationStockModel.query.get(
        item_stock_loc_1.id
    )
    stock_item_location_2 = InventoryItemLocationStockModel.query.get(
        item_stock_loc_2.id
    )
    assert stock_item_location_1 is not None
    assert stock_item_location_2 is not None
    assert stock_item_location_1.actual_stock == 1
    assert stock_item_location_2.actual_stock == 0


def test_delete_item_ok(db_session):
    item_model1 = __create_dummy_component_item(db_session)

    assert item_model1 is not None
    assert item_model1.id is not None

    inventory_service.delete_item(item_model1.id)

    item_model1 = InventoryItemModel.query.get(item_model1.id)
    assert item_model1 is None


def test_delete_location_ok(db_session):
    location_model_1 = InventoryLocationModel(
        name="location1", description="description1", dici="dummydici1"
    )
    db_session.add(location_model_1)
    db_session.commit()

    inventory_service.delete_stock_location(location_model_1.id)

    location_db_model = InventoryLocationModel.query.get(location_model_1.id)
    assert location_db_model is None


def test_get_locations_ok(db_session):
    location_model_1 = InventoryLocationModel(
        name="location1", description="description1", dici="dummydici1"
    )
    location_model_2 = InventoryLocationModel(
        name="location2", description="description2", dici="dummydici1"
    )
    location_model_3 = InventoryLocationModel(
        name="location3", description="description3", dici="dummydici1"
    )
    db_session.add(location_model_1)
    db_session.add(location_model_2)
    db_session.add(location_model_3)
    db_session.commit()

    page = inventory_service.get_locations(1, 4)
    assert page is not None
    assert page.pages == 1
    assert page.total == 3
    assert next((x for x in page.items if x.id == location_model_1.id), None)
    assert next((x for x in page.items if x.id == location_model_2.id), None)
    assert next((x for x in page.items if x.id == location_model_3.id), None)


def test_delete_item_category_ok(db_session):
    item_model = __create_dummy_component_item(db_session)
    category_model = InventoryCategoryModel(
        name="test name", description="test description"
    )
    db_session.add(category_model)
    db_session.commit()

    item_model.category_id = category_model.id
    item_model.category = category_model
    db_session.add(category_model)
    db_session.commit()

    category_model = InventoryCategoryModel.query.get(category_model.id)
    assert len(category_model.category_items) == 1
    assert next(
        (x for x in category_model.category_items if x.id == item_model.id), None
    )

    inventory_service.delete_item_category(item_model.id)

    category_model = InventoryCategoryModel.query.get(category_model.id)
    item_model = InventoryItemModel.query.get(item_model.id)
    assert len(category_model.category_items) == 0
    assert item_model.category_id is None


def test_update_item_location_stock_levels_ok(db_session):
    item_model, location_model = __get_create_item_location_and_stock(db_session, 1)
    item_stock_loc = __get_create_item_location_stock(
        db_session, item_model.id, location_model.id
    )

    inventory_service.update_item_location_stock_levels(
        item_model.id, location_model.id, 3, 1
    )
    stock_item_location_model = InventoryItemLocationStockModel.query.get(
        item_stock_loc.id
    )

    assert stock_item_location_model is not None
    assert stock_item_location_model.stock_notify_min_level == 1
    assert stock_item_location_model.stock_min_level == 3


def test_create_item_stocks_for_locations_ok(db_session):
    item_model_1, location_model_1 = __get_create_item_location_and_stock(db_session, 1)
    item_model_2, location_model_2 = __get_create_item_location_and_stock(db_session, 2)

    inventory_service.create_item_stocks_for_locations(
        item_model_1.id, [location_model_1.id, location_model_2.id]
    )
    inventory_service.create_item_stocks_for_locations(
        item_model_2.id, [location_model_2.id]
    )

    item_stock_1 = (
        InventoryItemLocationStockModel.query.filter(
            InventoryItemLocationStockModel.item_id == item_model_1.id
        )
        .filter(InventoryItemLocationStockModel.location_id == location_model_1.id)
        .one()
    )
    item_stock_2 = (
        InventoryItemLocationStockModel.query.filter(
            InventoryItemLocationStockModel.item_id == item_model_1.id
        )
        .filter(InventoryItemLocationStockModel.location_id == location_model_2.id)
        .one()
    )
    item_stock_3 = (
        InventoryItemLocationStockModel.query.filter(
            InventoryItemLocationStockModel.item_id == item_model_2.id
        )
        .filter(InventoryItemLocationStockModel.location_id == location_model_2.id)
        .one()
    )

    assert item_stock_1 is not None
    assert item_stock_1.stock_notify_min_level == -1
    assert item_stock_1.stock_min_level == 0
    assert item_stock_1.actual_stock == 0
    assert item_stock_2 is not None
    assert item_stock_2.stock_notify_min_level == -1
    assert item_stock_2.stock_min_level == 0
    assert item_stock_2.actual_stock == 0
    assert item_stock_3 is not None
    assert item_stock_3.stock_notify_min_level == -1
    assert item_stock_3.stock_min_level == 0
    assert item_stock_3.actual_stock == 0


def test_get_categories_ok(db_session):
    category_1 = __create_dummy_category(db_session, 1)
    category_2 = __create_dummy_category(db_session, 2)
    category_3 = __create_dummy_category(db_session, 3)
    category_4 = __create_dummy_category(db_session, 4)
    page = inventory_service.get_categories(1, 4, False)
    assert page is not None
    assert page.pages == 1
    assert next((x for x in page.items if x.id == category_1.id), None)
    assert next((x for x in page.items if x.id == category_2.id), None)
    assert next((x for x in page.items if x.id == category_3.id), None)
    assert next((x for x in page.items if x.id == category_4.id), None)


def test_get_category_items_ok(db_session):
    item_model1 = __create_dummy_component_item(db_session, mpn="mpn1")
    item_model2 = __create_dummy_component_item(db_session, mpn="mpn2")
    item_model3 = __create_dummy_component_item(db_session, mpn="mpn3")
    category_model1 = InventoryCategoryModel(
        name="test name 1", description="test description"
    )
    category_model2 = InventoryCategoryModel(
        name="test name 2", description="test description"
    )
    db_session.add(category_model1)
    db_session.add(category_model2)
    db_session.commit()

    item_model1.category_id = category_model1.id
    item_model2.category_id = category_model2.id
    item_model3.category_id = category_model2.id
    db_session.add(item_model1)
    db_session.add(item_model2)
    db_session.add(item_model3)
    db_session.commit()

    page = inventory_service.get_category_items(category_model1.id, 1, 4)
    assert page is not None
    assert page.pages == 1
    assert page.total == 1
    assert next((x for x in page.items if x.id == item_model1.id), None)

    page = inventory_service.get_category_items(category_model2.id, 1, 4)
    assert page is not None
    assert page.pages == 1
    assert page.total == 2
    assert next((x for x in page.items if x.id == item_model2.id), None)
    assert next((x for x in page.items if x.id == item_model3.id), None)


def test_get_location_ko(db_session):
    with pytest.raises(Exception) as e_info:
        inventory_service.get_location(34234324)

    assert e_info.type is ResourceNotFoundApiError
    assert e_info.value.missing_id == 34234324


def test_stock_mass_update_ko(db_session):
    item_model_1, location_model_1 = __get_create_item_location_and_stock(db_session, 1)
    item_model_2, location_model_2 = __get_create_item_location_and_stock(db_session, 2)

    # Invalid item ID
    movement = MassStockMovement(
        reason="test move",
        comment="test comment",
        movements=[
            SingleStockMovement(
                item_id=12345, location_id=location_model_1.id, quantity=3
            ),
            SingleStockMovement(
                item_id=item_model_2.id, location_id=location_model_2.id, quantity=1
            ),
        ],
    )

    with pytest.raises(Exception) as e_info:
        inventory_service.stock_mass_update(movement)

    assert e_info.type is ResourceNotFoundApiError
    assert e_info.value.missing_id == 12345

    # Invalid location ID
    movement = MassStockMovement(
        reason="test move",
        comment="test comment",
        movements=[
            SingleStockMovement(
                item_id=item_model_1.id, location_dici="sdasdas33", quantity=3
            ),
            SingleStockMovement(
                item_id=item_model_2.id, location_id=location_model_2.id, quantity=1
            ),
        ],
    )

    with pytest.raises(Exception) as e_info:
        inventory_service.stock_mass_update(movement)

    assert e_info.type is ResourceNotFoundApiError
    assert e_info.value.missing_dici == "sdasdas33"

    # Invalid line without ID or DICI for the item
    movement = MassStockMovement(
        reason="test move",
        comment="test comment",
        movements=[
            SingleStockMovement(
                item_id=None,
                item_dici=None,
                location_dici=location_model_1.dici,
                quantity=3,
            ),
            SingleStockMovement(
                item_id=item_model_2.id, location_id=location_model_2.id, quantity=1
            ),
        ],
    )

    with pytest.raises(Exception) as e_info:
        inventory_service.stock_mass_update(movement)

    assert e_info.type is InvalidMassStockUpdateError

    # Invalid line without ID or DICI for the location
    movement = MassStockMovement(
        reason="test move",
        comment="test comment",
        movements=[
            SingleStockMovement(
                item_id=item_model_1.id,
                location_dici=None,
                location_id=None,
                quantity=3,
            ),
            SingleStockMovement(
                item_id=item_model_2.id, location_id=location_model_2.id, quantity=1
            ),
        ],
    )

    with pytest.raises(Exception) as e_info:
        inventory_service.stock_mass_update(movement)

    assert e_info.type is InvalidMassStockUpdateError

    # Invalid line without previously created item-location stock relation
    movement = MassStockMovement(
        reason="test move",
        comment="test comment",
        movements=[
            SingleStockMovement(
                item_id=item_model_1.id, location_id=location_model_1.id, quantity=3
            ),
            SingleStockMovement(
                item_id=item_model_2.id, location_id=location_model_2.id, quantity=1
            ),
        ],
    )

    with pytest.raises(Exception) as e_info:
        inventory_service.stock_mass_update(movement)

    assert e_info.type is ResourceNotFoundApiError

    # Try to retreive more than the minimum stock level
    item_stock_loc_1 = __get_create_item_location_stock(
        db_session, item_model_1.id, location_model_1.id, quantity=4
    )
    item_stock_loc_2 = __get_create_item_location_stock(
        db_session, item_model_2.id, location_model_2.id, quantity=3
    )

    movement = MassStockMovement(
        reason="test move",
        comment="test comment",
        movements=[
            SingleStockMovement(
                item_id=item_model_1.id, location_id=location_model_1.id, quantity=-3
            ),
            SingleStockMovement(
                item_id=item_model_2.id, location_id=location_model_2.id, quantity=-8
            ),
        ],
    )

    with pytest.raises(Exception) as e_info:
        inventory_service.stock_mass_update(movement)

    assert e_info.type is InvalidMassStockUpdateError
    stock_item_location_1 = InventoryItemLocationStockModel.query.get(
        item_stock_loc_1.id
    )
    stock_item_location_2 = InventoryItemLocationStockModel.query.get(
        item_stock_loc_2.id
    )
    assert stock_item_location_1 is not None
    assert stock_item_location_2 is not None
    assert stock_item_location_1.actual_stock == 4
    assert stock_item_location_2.actual_stock == 3


def test_get_item_component_ok(db_session):
    item_model1 = __create_dummy_component_item(db_session, mpn="mpn1")
    component = inventory_service.get_item_component(item_model1.id)
    assert component is not None


def test_get_item_component_ko(db_session):
    item_model1 = __create_dummy_standalone_item(
        db_session, mpn="mpn1", manufacturer="test_man"
    )
    with pytest.raises(Exception) as e_info:
        inventory_service.get_item_component(item_model1.id)
    assert e_info.type is ResourceNotFoundApiError
    with pytest.raises(Exception) as e_info:
        inventory_service.get_item_component(12345)
    assert e_info.type is ResourceNotFoundApiError
    assert e_info.value.missing_id == 12345
