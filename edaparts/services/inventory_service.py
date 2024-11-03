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


import logging
import random
import string
import typing

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql.functions import func

from edaparts.models.components.component_model import ComponentModel
from edaparts.models.internal.internal_inventory_models import (
    InventoryItemStockStatus,
    MassStockMovement,
)
from edaparts.models.inventory.inventory_category_model import InventoryCategoryModel
from edaparts.models.inventory.inventory_identificable_item_model import (
    InventoryIdentificableItemModel,
)
from edaparts.models.inventory.inventory_item_location_stock import (
    InventoryItemLocationStockModel,
)
from edaparts.models.inventory.inventory_item_model import InventoryItemModel
from edaparts.models.inventory.inventory_item_property import InventoryItemPropertyModel
from edaparts.models.inventory.inventory_item_stock_movement import (
    InventoryItemLocationStockMovementModel,
)
from edaparts.models.inventory.inventory_location import InventoryLocationModel
from edaparts.services.exceptions import (
    ResourceAlreadyExistsApiError,
    UniqueIdentifierCreationError,
    ResourceNotFoundApiError,
    RemainingStocksExistError,
    InvalidMassStockUpdateError,
    CyclicCategoryDependecy,
    InvalidCategoryRelationError,
)
from edaparts.utils.helpers import BraceMessage as __l

__logger = logging.getLogger(__name__)


async def __search_item_location_stock_by_ids_dicis(
    db: AsyncSession, item_id: int | str, location_id: str | int
) -> InventoryItemLocationStockModel:
    item_filters = []
    location_filters = []
    if isinstance(location_id, int):
        location_filters.append(InventoryLocationModel.id == location_id)
    else:
        location_filters.append(InventoryLocationModel.dici == location_id)

    if isinstance(item_id, int):
        item_filters.append(InventoryItemModel.id == item_id)
    else:
        item_filters.append(InventoryItemModel.dici == item_id)

    try:
        return (
            await db.scalars(
                select(InventoryItemLocationStockModel)
                .join(InventoryItemModel)
                .join(InventoryLocationModel)
                .filter(*(item_filters + location_filters))
                .options(joinedload(InventoryItemLocationStockModel.item))
                .options(joinedload(InventoryItemLocationStockModel.location))
            )
        ).one()

    except NoResultFound:
        if not (
            await db.scalars(select(InventoryItemModel).filter(*item_filters))
        ).first():
            # Item not exist
            raise ResourceNotFoundApiError(
                "Item doesn't exist",
                missing_dici=(item_id if isinstance(item_id, str) else None),
                missing_id=(item_id if isinstance(item_id, int) else None),
            )

        if not (
            await db.scalars(select(InventoryLocationModel).filter(*location_filters))
        ).first():
            # Location not exist
            raise ResourceNotFoundApiError(
                "Location doesn't exist",
                missing_dici=(location_id if isinstance(location_id, str) else None),
                missing_id=(location_id if isinstance(location_id, int) else None),
            )

        raise ResourceNotFoundApiError(
            "The given location and item has no item location stock relation"
        )

    except MultipleResultsFound:
        raise InvalidMassStockUpdateError("Internal integrity error")


def __update_item_location_stock(
    stock_item: InventoryItemLocationStockModel, quantity: float, reason: str
) -> InventoryItemLocationStockMovementModel:
    if stock_item.stock_min_level <= (stock_item.actual_stock + quantity):
        stock_item.actual_stock = stock_item.actual_stock + quantity
        stock_item_movement = InventoryItemLocationStockMovementModel(
            stock_change=quantity, reason=reason, stock_item_id=stock_item.id
        )
        return stock_item_movement

    raise InvalidMassStockUpdateError(
        __l(
            "Item has reached its minimum stock level [item_dici={0}, location_dici={1}]",
            stock_item.item.dici,
            stock_item.location.dici,
        )
    )


async def __get_item_location_stock(
    db: AsyncSession, item_id: int, location_id: int
) -> InventoryItemLocationStockModel:
    item_stock = (
        await db.scalars(
            select(InventoryItemLocationStockModel).filter_by(
                item_id=item_id, location_id=location_id
            )
        )
    ).first()

    # Verify that the given item exists before trying anything else
    if not item_stock:

        # Try to raise a fine grade exception instead of the simplest one
        if not await db.get(InventoryItemModel, item_id):
            raise ResourceNotFoundApiError(
                "Inventory item not found", missing_id=item_id
            )
        if not await db.get(InventoryLocationModel, location_id):
            raise ResourceNotFoundApiError(
                "Inventory location not found", missing_id=location_id
            )

    return item_stock


async def __check_item_existence(db: AsyncSession, item_id: int):
    return (
        await db.scalars(select(InventoryItemModel.id).filter_by(id=item_id).limit(1))
    ).first() is not None


def __recursive_parent_search(
    ids_to_avoid: list[int], category: InventoryCategoryModel
):
    if category.id in ids_to_avoid:
        raise CyclicCategoryDependecy(
            __l(
                "Category {0} association will cause a cyclic category tree",
                ids_to_avoid,
            )
        )
    ids_to_avoid.append(category.id)
    for child in category.children:
        __recursive_parent_search(ids_to_avoid, child)


async def create_item_for_component(
    db: AsyncSession, component_model: ComponentModel
) -> InventoryItemModel:
    exists_id = (
        await db.scalars(
            select(InventoryItemModel.id)
            .filter_by(
                mpn=component_model.mpn, manufacturer=component_model.manufacturer
            )
            .limit(1)
        )
    ).first()
    if exists_id:
        raise ResourceAlreadyExistsApiError(
            msg="An item already exists for the given component",
            conflicting_id=exists_id,
        )
    dici_id = await generate_item_id(db, obj_model=component_model)
    item_model = InventoryItemModel(
        dici=dici_id,
        mpn=component_model.mpn,
        manufacturer=component_model.manufacturer,
        name=component_model.mpn,
        description=component_model.description,
        last_buy_price=0.0,
        component_id=component_model.id,
        component=component_model,
    )

    db.add(item_model)
    # Do not commit, this method is called from a session that will commit in the caller

    __logger.debug(
        __l("Inventory item created [id={0}, dici={1}]", item_model.id, item_model.dici)
    )
    return item_model


async def create_standalone_item(
    db: AsyncSession, model: InventoryItemModel
) -> InventoryItemModel:
    exists_id = (
        await db.scalars(
            select(InventoryItemModel.id)
            .filter_by(mpn=model.mpn, manufacturer=model.manufacturer)
            .limit(1)
        )
    ).first()
    if exists_id:
        raise ResourceAlreadyExistsApiError(
            msg="An item already exists for the given item", conflicting_id=exists_id
        )
    dici = await generate_item_id(db)
    item_model = InventoryItemModel(
        dici=dici,
        mpn=model.mpn,
        manufacturer=model.manufacturer,
        name=model.name,
        description=model.description,
        last_buy_price=0.0,
    )

    db.add(item_model)
    await db.commit()

    __logger.debug(
        __l("Inventory item created [id={0}, dici={1}]", item_model.id, item_model.dici)
    )
    return item_model


async def get_item(
    db: AsyncSession, item_id: int, load_component: bool = False
) -> InventoryItemModel:
    __logger.debug(__l("Querying item data [item_id={0}]", item_id))

    query = select(InventoryItemModel).filter_by(id=item_id).limit(1)
    if load_component:
        query = query.options(selectinload(InventoryItemModel.component))
    result = (await db.scalars(query)).first()

    if not result:
        raise ResourceNotFoundApiError("Item not found", missing_id=item_id)
    return result


async def create_location(
    db: AsyncSession, name: str, description: str = None
) -> InventoryLocationModel:
    # Check if a location with the given name already exists
    current_location_result = await db.scalars(
        select(InventoryLocationModel.id).filter_by(name=name).limit(1)
    )
    current_id = current_location_result.first()
    if current_id:
        raise ResourceAlreadyExistsApiError(
            __l("Location with name {0} already exists", name),
            conflicting_id=current_id,
        )

    location = InventoryLocationModel(name=name, description=description)
    location.dici = await generate_item_id(db, obj_model=location)

    db.add(location)
    await db.commit()
    __logger.debug(
        __l("Inventory location created [id={0}, dici={1}]", location.id, location.dici)
    )
    return location


async def get_location(db: AsyncSession, location_id: int) -> InventoryLocationModel:
    __logger.debug(__l("Querying location [location_id={0}]", location_id))
    location = await db.get(InventoryLocationModel, location_id)
    if not location:
        raise ResourceNotFoundApiError("Location not found", missing_id=location_id)
    # todo investigate types missmatch
    return location


async def get_locations(
    db: AsyncSession, page_number: int, page_size: int
) -> typing.Tuple[typing.Sequence[InventoryLocationModel], int]:
    __logger.debug(
        __l("Retrieving locations [page_n={0}, page_size={1}]", page_number, page_size)
    )
    query = (
        select(InventoryLocationModel)
        .limit(page_size)
        .offset((page_number - 1) * page_size)
        .order_by(InventoryLocationModel.id.desc())
    )
    result_page = await db.execute(query)
    # todo: use one single query
    total_count = await db.scalar(
        select(func.count()).select_from(InventoryLocationModel)
    )
    return result_page.scalars().all(), total_count


async def get_category_items(
    db: AsyncSession,
    category_id: int,
    page_number: int,
    page_size: int,
    load_component: bool = False,
) -> typing.Tuple[typing.Sequence[InventoryItemModel], int]:
    __logger.debug(
        __l(
            "Retrieving category items [category_id={0}, page_n={1}, page_size={2}]",
            category_id,
            page_number,
            page_size,
        )
    )
    db_category_id = (
        await db.scalars(
            select(InventoryCategoryModel.id).filter_by(id=category_id).limit(1)
        )
    ).first()
    if not db_category_id:
        raise ResourceNotFoundApiError("Category not found", missing_id=category_id)

    query = select(InventoryItemModel).filter_by(category_id=category_id)
    query = (
        query.options(joinedload(InventoryItemModel.component))
        if load_component
        else query
    )
    query = (
        query.order_by(InventoryItemModel.id.desc())
        .limit(page_size)
        .offset((page_number - 1) * page_size)
    )

    # todo: extract to common place
    _count_column_name = "__private_edaparts_get_category_items_row_count"
    new_query = query.add_columns(func.count().over().label(_count_column_name))
    rows_result = (await db.execute(new_query)).fetchall()
    results = []
    total = 0
    for index in range(len(rows_result)):
        row_data = rows_result[index]
        if index == 0:
            total = row_data[1]
        results.append(row_data[0])
    return results, total


async def create_item_stocks_for_locations(
    db: AsyncSession, item_id: int, location_ids: list[int | str]
) -> list[int]:
    __logger.debug(
        __l(
            "Creating new item-location relations [item_id={0}, location_ids={1}]",
            item_id,
            location_ids,
        )
    )

    item = (
        await db.scalars(
            select(InventoryItemModel)
            .filter_by(id=item_id)
            .limit(1)
            .options(joinedload(InventoryItemModel.stock_items))
        )
    ).first()
    if not item:
        raise ResourceNotFoundApiError("Item not found", missing_id=item_id)

    item_stocks = []
    item_stock_per_location = {
        item_stock.location_id: item_stock for item_stock in item.stock_items
    }
    try:
        for location_id in location_ids:
            db_location_id = (
                await db.scalars(
                    select(InventoryLocationModel.id)
                    .filter_by(
                        **{
                            (
                                "dici" if isinstance(location_id, str) else "id"
                            ): location_id
                        }
                    )
                    .limit(1)
                )
            ).first()
            if not db_location_id:
                raise ResourceNotFoundApiError(
                    "Inventory location not found", missing_id=location_id
                )

            if db_location_id in item_stock_per_location:
                # skip, it already exists
                continue

            # Create a freshly new stock item for the location
            item_stock = InventoryItemLocationStockModel(
                actual_stock=0,
                stock_min_level=0,
                stock_notify_min_level=-1.0,
                location_id=db_location_id,
                item_id=item.id,
            )
            item_stocks.append(item_stock)
            item_stock_per_location[db_location_id] = item_stock
            db.add(item_stock)

        await db.commit()
    except:
        await db.rollback()
        raise

    __logger.debug(
        __l(
            "Item locations updated [item_id={0}, location_ids={1}]",
            item_id,
            location_ids,
        )
    )
    return [cfr.location_id for cfr in item_stocks]


async def delete_stock_location(db: AsyncSession, location_id: int):
    location = await db.get(InventoryLocationModel, location_id)
    if location:
        if len([si for si in location.stock_items if si.actual_stock != 0]) > 0:
            raise RemainingStocksExistError("Location still contains available stocks")
        try:
            for stock_item in location.stock_items:
                await db.delete(stock_item)

            await db.delete(location)
            await db.commit()
        # todo: Add a more specific exception
        except:
            await db.rollback()
        __logger.debug(__l("Removed location [location_id={0}]", location_id))


async def delete_item(db: AsyncSession, item_id: int):
    query = (
        select(InventoryItemModel)
        .filter_by(id=item_id)
        .options(selectinload(InventoryItemModel.stock_items))
        .limit(1)
    )
    item = (await db.scalars(query)).first()
    if item:
        if len([si for si in item.stock_items if si.actual_stock != 0]) > 0:
            raise RemainingStocksExistError("Item still contains available stocks")

        try:
            for stock_item in item.stock_items:
                # This should trigger the cascade delete of the movements history
                await db.delete(stock_item)

            await db.delete(item)
            await db.commit()

        except:
            await db.rollback()

        __logger.debug(__l("Removed item [item_id={0}]", item_id))


async def get_item_stock_for_location(db: AsyncSession, item_id: int, location_id: int):
    __logger.debug(
        __l(
            "Retrieving item stock for location [item_id={0}, location_id={1}]",
            item_id,
            location_id,
        )
    )

    return await __get_item_location_stock(db, item_id, location_id)


async def update_item_location_stock_levels(
    db: AsyncSession,
    item_id: int,
    location_id: int,
    min_stock_level=None,
    min_notify_level=None,
) -> InventoryItemLocationStockModel:
    __logger.debug(
        __l(
            "Updating item stock for location [item_id={0}, location_id={1}, min_stock_level={2}, min_notify_level={3}]",
            item_id,
            location_id,
            min_stock_level,
            min_notify_level,
        )
    )

    item_stock = await __get_item_location_stock(db, item_id, location_id)
    if (min_stock_level is not None) and min_stock_level >= -1.0:
        item_stock.stock_min_level = min_stock_level
    if (min_notify_level is not None) and min_notify_level > -1.0:
        item_stock.stock_notify_min_level = min_notify_level

    db.add(item_stock)
    await db.commit()
    return item_stock


async def stock_mass_update(
    db: AsyncSession, mass_stock_update: MassStockMovement
) -> list[InventoryItemStockStatus]:
    stock_status_lines = []
    try:
        for itm in mass_stock_update.movements:
            # Search the stock item location model by item/location id or dici
            stock_item = await __search_item_location_stock_by_ids_dicis(
                db,
                item_id=itm.item_identifier,
                location_id=itm.location_identifier,
            )

            # Annotate the stock movement
            movement_entry = __update_item_location_stock(
                stock_item, itm.quantity, mass_stock_update.reason
            )

            # Add DB changes to be persisted
            db.add(movement_entry)
            db.add(stock_item)

            # Append the change to a list to return the actual stock level to caller
            stock_status_lines.append(
                InventoryItemStockStatus(
                    stock_level=stock_item.actual_stock,
                    item_dici=stock_item.item.dici,
                    location_dici=stock_item.location.dici,
                )
            )

        # Persist all the changes
        await db.commit()

        __logger.debug(
            __l(
                "Mass stock update done. {0} update movements executed.",
                len(stock_status_lines),
            )
        )

        return stock_status_lines
    except Exception as err:
        __logger.debug(__l("Mass stock aborted by {0}", err.__class__.__name__))

        # If a single operation goes wrong just rollback all changes
        await db.rollback()
        raise


async def add_property_to_item(
    db: AsyncSession, item_id: int, property_model
) -> InventoryItemPropertyModel:
    __logger.debug(
        __l(
            "Adding property to item [item_id={0}, property_name={1},]",
            item_id,
            property_model.property_name,
        )
    )
    if not await __check_item_existence(db, item_id):
        raise ResourceNotFoundApiError("Inventory item not found", missing_id=item_id)

    prop = (
        await db.scalars(
            select(InventoryItemPropertyModel)
            .filter_by(property_name=property_model.property_name, item_id=item_id)
            .limit(1)
        )
    ).first()
    if prop:
        # Already exists
        raise ResourceAlreadyExistsApiError(
            "Property already exists", conflicting_id=prop.id
        )

    property_model.item_id = item_id
    db.add(property_model)
    await db.commit()

    return property_model


async def update_item_property(
    db: AsyncSession, item_id: int, property_id: int, new_value: str | float | int
) -> InventoryItemPropertyModel:
    __logger.debug(
        __l(
            "Updating item property [item_id={0}, property_id={1}]",
            item_id,
            property_id,
        )
    )

    prop = await db.get(InventoryItemPropertyModel, property_id)
    if not prop:
        # Property not exists
        raise ResourceNotFoundApiError(
            "Inventory property not found", missing_id=property_id
        )

    # Update model value
    prop.set_value(new_value)

    # Persist to DB
    db.add(prop)
    await db.commit()

    return prop


async def get_item_properties(
    db: AsyncSession, item_id: int
) -> list[InventoryItemPropertyModel]:
    __logger.debug(__l("Retrieving item properties [item_id={0}]", item_id))

    query = (
        select(InventoryItemModel)
        .filter_by(id=item_id)
        .options(selectinload(InventoryItemModel.item_properties))
        .limit(1)
    )
    result = (await db.scalars(query)).first()

    if not result:
        raise ResourceNotFoundApiError("Item not found", missing_id=item_id)

    return result.item_properties


async def delete_item_property(db: AsyncSession, item_id: int, property_id: int):
    __logger.debug(
        __l(
            "Removing item property [item_id={0}, property_id={1}]",
            item_id,
            property_id,
        )
    )
    prop = await db.get(InventoryItemPropertyModel, property_id)
    if prop:
        await db.delete(prop)
        await db.commit()


async def create_category(
    db: AsyncSession, name: str, description
) -> InventoryCategoryModel:
    __logger.debug(
        __l("Creating category [name={0}, description={1}]", name, description)
    )

    category = InventoryCategoryModel(name=name, description=description)
    current_category = (
        await db.scalars(select(InventoryCategoryModel).filter_by(name=name).limit(1))
    ).first()
    if current_category:
        raise ResourceAlreadyExistsApiError(
            __l("Category with name {0} already exists", name),
            conflicting_id=current_category.id,
        )

    db.add(category)
    await db.commit()

    __logger.debug(__l("Inventory category created [id={0}]", category.id))
    return category


async def get_category(db: AsyncSession, category_id: int) -> InventoryCategoryModel:
    __logger.debug(__l("Querying category [category_id={0}]", category_id))
    category = await db.get(InventoryCategoryModel, category_id)
    if not category:
        raise ResourceNotFoundApiError("Category not found", missing_id=category_id)
    return category


async def get_categories(
    db: AsyncSession, page_number: int, page_size: int, only_root: bool = False
) -> typing.Tuple[list[InventoryCategoryModel], int]:
    __logger.debug("Retrieving categories")

    query = select(InventoryCategoryModel)
    query = query.filter_by(parent_id=None) if only_root else query
    query = (
        query.order_by(InventoryCategoryModel.id.desc())
        .limit(page_size)
        .offset((page_number - 1) * page_size)
    )

    # todo: extract to common place
    _count_column_name = "__private_edaparts_search_items_row_count"
    new_query = query.add_columns(func.count().over().label(_count_column_name))
    rows_result = (await db.execute(new_query)).fetchall()
    results = []
    total = 0
    for index in range(len(rows_result)):
        row_data = rows_result[index]
        if index == 0:
            total = row_data[1]
        results.append(row_data[0])
    return results, total


async def set_category_parent(
    db: AsyncSession, category_id: int, parent_id: int
) -> InventoryCategoryModel:
    __logger.debug(
        __l(
            "Updating category parent [category_id={0}, parent_id={1}]",
            category_id,
            parent_id,
        )
    )
    category = await db.get(InventoryCategoryModel, category_id)
    if not category:
        raise ResourceNotFoundApiError("Category not found", missing_id=category_id)

    if not parent_id:
        raise InvalidCategoryRelationError(
            "Parent ID cannot be null. Use delete method to delete the relation"
        )

    parent = (
        await db.scalars(
            select(InventoryCategoryModel)
            .filter_by(id=parent_id)
            .options(joinedload(InventoryCategoryModel.children))
        )
    ).first()
    if not parent:
        raise ResourceNotFoundApiError("Category not found", missing_id=parent_id)

    __recursive_parent_search([category_id], parent)

    category.parent_id = parent_id

    db.add(category)
    await db.commit()
    return category


async def remove_category_parent(db: AsyncSession, category_id: int):
    __logger.debug(__l("Removing category parent [category_id={0}]", category_id))
    category = await db.get(InventoryCategoryModel, category_id)
    if not category:
        raise ResourceNotFoundApiError("Category not found", missing_id=category_id)

    if category.parent_id:
        category.parent_id = None
        db.add(category)
        await db.commit()


async def update_category(
    db: AsyncSession, category_id: int, name: str, description: str = None
) -> InventoryCategoryModel:
    __logger.debug(
        __l(
            "Updating category [category_id={0}, name={1}, description={2}]",
            category_id,
            name,
            description,
        )
    )
    category = await db.get(InventoryCategoryModel, category_id)
    if not category:
        raise ResourceNotFoundApiError("Category not found", missing_id=category_id)

    if name != category.name:
        select(InventoryCategoryModel.id).filter_by(name=name).limit(1)
        query = select(InventoryCategoryModel.id).filter_by(name=name).limit(1)
        current_category_id = (await db.scalars(query)).first()
        if current_category_id:
            raise ResourceAlreadyExistsApiError(
                __l("Category with name {0} already exists", name),
                conflicting_id=current_category_id,
            )

        category.name = name
    category.description = description

    db.add(category)
    await db.commit()

    return category


async def set_item_category(db: AsyncSession, item_id: int, category_id: int):
    __logger.debug(
        __l(
            "Setting item category [item_id={1}, category_id={0}]", item_id, category_id
        )
    )

    category_id = (
        await db.scalars(
            select(InventoryCategoryModel.id).filter_by(id=category_id).limit(1)
        )
    ).first()
    if not category_id:
        raise ResourceNotFoundApiError("Category not found", missing_id=category_id)

    item = await db.get(InventoryItemModel, item_id)
    if not item:
        raise ResourceNotFoundApiError("Item not found", missing_id=item_id)

    item.category_id = category_id

    db.add(item)
    await db.commit()


async def delete_item_category(db: AsyncSession, item_id: int):
    __logger.debug(__l("Deleting category from item [item_id={0}]", item_id))

    item = await db.get(InventoryItemModel, item_id)
    if not item:
        raise ResourceNotFoundApiError("Item not found", missing_id=item_id)

    item.category_id = None

    db.add(item)
    await db.commit()


def __id_generator(size=10, chars=None) -> str:
    return "".join(
        random.choice(chars or (string.ascii_uppercase + string.digits))
        for _ in range(size)
    )


async def generate_item_id(db: AsyncSession, obj_model=None):
    if isinstance(obj_model, InventoryIdentificableItemModel):
        query_obj = None
        if isinstance(obj_model, InventoryItemModel) or isinstance(
            obj_model, ComponentModel
        ):
            query_obj = InventoryItemModel
        elif isinstance(obj_model, InventoryLocationModel):
            query_obj = InventoryLocationModel

        if query_obj:
            model_prefix = obj_model.get_id_prefix()
            for x in range(3):
                gen_dici = model_prefix + "-" + __id_generator()
                existing_dici_result = await db.scalars(
                    select(query_obj.dici).filter_by(dici=gen_dici).limit(1)
                )
                current_id = existing_dici_result.first()
                if not current_id:
                    return gen_dici
    else:
        return "ITEM-" + __id_generator()

    raise UniqueIdentifierCreationError(
        "Cannot create a unique identifier for an inventory item"
    )
