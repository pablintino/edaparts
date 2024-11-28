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
import typing

from sqlalchemy import select, func, inspect, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from edaparts.models.components import ComponentModelType
from edaparts.models.components.component_model import ComponentModel
from edaparts.models.libraries.footprint_reference_model import FootprintReference
from edaparts.models.libraries.join_tables import (
    component_footprint_asc_table,
    component_library_asc_table,
)
from edaparts.models.libraries.library_reference_model import LibraryReference
from edaparts.services import inventory_service
from edaparts.services.exceptions import (
    ResourceAlreadyExistsApiError,
    ResourceNotFoundApiError,
    InvalidComponentFieldsError,
    RelationExistsError,
)
from edaparts.utils.helpers import BraceMessage as __l
from edaparts.utils.sqlalchemy import query_page

__logger = logging.getLogger(__name__)


def __validate_update_component_model(
    model: ComponentModelType, candidate_model: ComponentModelType
):
    if model.type != candidate_model.type:
        raise InvalidComponentFieldsError(
            f"Component type cannot be changed. Existing component type: {model.type}",
            reserved_fields="type",
        )
    reserved_field_names = ["created_on", "updated_on", "id", "mpn", "manufacturer"]
    candidate_inspect = inspect(candidate_model)
    present_fields = [
        data
        for name, data in candidate_inspect.attrs.items()
        if name in reserved_field_names
    ]
    invalid_fields = [field for field in present_fields if field.value is not None]
    if invalid_fields:
        raise InvalidComponentFieldsError(
            "Update reserved fields were provided", reserved_fields=invalid_fields
        )
    relationship_fields = candidate_inspect.mapper.relationships
    to_map_fields = set(candidate_inspect.attrs.keys()) - set(
        reserved_field_names + ["type"]
    )
    # Compute the columns that are used for relationships and discard them
    for name, data in relationship_fields.items():
        for relation_col in (col.key for col in data.local_columns):
            to_map_fields.discard(relation_col)
        to_map_fields.discard(name)

    # Update the fields in the target model
    for name, attr in candidate_inspect.attrs.items():
        if name not in to_map_fields:
            continue
        setattr(model, name, getattr(candidate_model, name))


async def create_component[T: ComponentModelType](db: AsyncSession, model: T) -> T:
    __logger.debug(
        __l(
            "Creating component [mpn={0}, manufacturer={1}]",
            model.mpn,
            model.manufacturer,
        )
    )
    exists_id = (
        await db.scalars(
            select(ComponentModel.id)
            .filter_by(mpn=model.mpn, manufacturer=model.manufacturer)
            .limit(1)
        )
    ).first()
    if exists_id:
        raise ResourceAlreadyExistsApiError(
            "Cannot create the requested component cause it already exists",
            conflicting_id=exists_id,
        )
    try:
        db.add(model)

        # Create inventory item automatically
        await inventory_service.create_item_for_component(db, model)
        await db.commit()

    except:
        await db.rollback()
        raise
    __logger.debug(__l("Component created [id={0}]", model.id))
    return model


async def update_component(
    db: AsyncSession, component_id: int, model: ComponentModelType
) -> ComponentModelType:
    __logger.debug(__l("Updating component [component_id={0}]", component_id))

    current_model = await db.get(ComponentModel, component_id)

    # Validate and update the model
    __validate_update_component_model(current_model, model)
    await db.commit()
    __logger.debug(
        __l(
            "Component updated [id={0}, mpn={1}, manufacturer={2}]",
            model.id,
            model.mpn,
            model.manufacturer,
        )
    )

    # refresh required to load update_on changes after commiting
    await db.refresh(current_model)
    return current_model


async def create_symbol_relation(
    db: AsyncSession, component_id: int, symbol_ids: list[int]
):
    __logger.debug(
        __l(
            "Creating new component-symbol relation [component_id={0}, symbol_ids={1}]",
            component_id,
            symbol_ids,
        )
    )

    component = await db.get(ComponentModel, component_id)
    if not component:
        raise ResourceNotFoundApiError("Component not found", missing_id=component_id)

    # Use the many-to-many table directly instead of ORM relation to avoid
    # the slow load of the SQL query that joins all component tables
    existing_library_ids = list(
        (
            await db.scalars(
                select(component_library_asc_table.c.library_ref_id).filter(
                    component_library_asc_table.c.component_id == component_id
                )
            )
        ).fetchall()
    )

    # Add only the symbols that are not already associated
    library_ids_to_add = [
        library_id
        for library_id in symbol_ids
        if library_id not in existing_library_ids
    ]
    if not library_ids_to_add:
        return sorted(library_ids_to_add)

    symbol_refs = []
    for symbol_id in library_ids_to_add:
        symbol_ref = await db.get(LibraryReference, symbol_id)
        if not symbol_ref:
            raise ResourceNotFoundApiError("Symbol not found", missing_id=symbol_id)
        symbol_refs.append(
            {"library_ref_id": symbol_ref.id, "component_id": component_id}
        )

    await db.execute(insert(component_library_asc_table), symbol_refs)
    await db.commit()
    __logger.debug(
        __l(
            "Component symbols updated [component_id={0}, symbol_ids={1}",
            component_id,
            symbol_ids,
        )
    )
    return list(sorted(dict.fromkeys(existing_library_ids + library_ids_to_add)))


async def create_footprints_relation(
    db: AsyncSession, component_id: int, footprint_ids: list[int]
) -> list[int]:
    __logger.debug(
        __l(
            "Creating new component-footprint relation [component_id={0}, footprint_ids={1}]",
            component_id,
            footprint_ids,
        )
    )

    component = await db.get(ComponentModel, component_id)
    if not component:
        raise ResourceNotFoundApiError("Component not found", missing_id=component_id)

    # Use the many-to-many table directly instead of ORM relation to avoid
    # the slow load of the SQL query that joins all component tables
    existing_footprints_ids = list(
        (
            await db.scalars(
                select(component_footprint_asc_table.c.footprint_ref_id).filter(
                    component_footprint_asc_table.c.component_id == component_id
                )
            )
        ).fetchall()
    )

    # Add only the footprints that are not already associated
    footprints_to_add = [
        foot_id for foot_id in footprint_ids if foot_id not in existing_footprints_ids
    ]
    if not footprints_to_add:
        return sorted(existing_footprints_ids)

    footprint_refs = []
    for footprint_id in footprints_to_add:
        footprint_ref = await db.get(FootprintReference, footprint_id)
        if not footprint_ref:
            raise ResourceNotFoundApiError(
                "Footprint not found", missing_id=footprint_id
            )
        footprint_refs.append(
            {"footprint_ref_id": footprint_ref.id, "component_id": component_id}
        )

    await db.execute(insert(component_footprint_asc_table), footprint_refs)
    await db.commit()
    __logger.debug(
        __l(
            "Component footprints updated [component_id={0}, footprint_ids={1}",
            component_id,
            footprint_ids,
        )
    )
    return list(sorted(dict.fromkeys(existing_footprints_ids + footprints_to_add)))


async def get_component_symbol_relations(
    db: AsyncSession, component_id
) -> typing.Sequence[LibraryReference]:
    __logger.debug(
        __l("Querying symbol relations for component [component_id={0}]", component_id)
    )
    component = await db.get(ComponentModel, component_id)
    if not component:
        raise ResourceNotFoundApiError("Component not found", missing_id=component_id)

    return (
        await db.scalars(
            select(LibraryReference)
            .join(LibraryReference.components_l)
            .filter_by(id=component_id)
        )
    ).all()


async def get_component_footprint_relations(
    db: AsyncSession, component_id: int
) -> typing.Sequence[FootprintReference]:
    __logger.debug(
        __l(
            "Querying footprint relations for component [component_id={0}]",
            component_id,
        )
    )
    component = await db.get(ComponentModel, component_id)
    if not component:
        raise ResourceNotFoundApiError("Component not found", missing_id=component_id)

    return (
        await db.scalars(
            select(FootprintReference)
            .join(FootprintReference.components_f)
            .filter_by(id=component_id)
        )
    ).all()


async def get_component(db: AsyncSession, component_id: int) -> ComponentModel:
    __logger.debug(__l("Querying component data [component_id={0}]", component_id))
    component = await db.get(ComponentModel, component_id)
    if not component:
        raise ResourceNotFoundApiError("Component not found", missing_id=component_id)
    return component


async def get_component_list(
    db: AsyncSession, page_number: int, page_size: int
) -> typing.Tuple[typing.Sequence[ComponentModel], int]:
    __logger.debug(
        __l(
            "Listing components for [page_number={0}, page_size={1}]",
            page_number,
            page_size,
        )
    )

    query = (
        select(ComponentModel)
        .limit(page_size)
        .offset((page_number - 1) * page_size)
        .order_by(ComponentModel.id.desc())
    )
    return await query_page(db, query)


async def delete_component(db: AsyncSession, component_id: int):
    __logger.debug(__l("Deleting component [component_id={0}]", component_id))
    component = (
        await db.scalars(
            select(ComponentModel)
            .filter_by(id=component_id)
            .options(selectinload(ComponentModel.inventory_item))
            .limit(1)
        )
    ).first()
    if component:
        if component.inventory_item:
            # todo: Improve exception details
            raise RelationExistsError("an inventory item exists for the component")

        await db.delete(component)
        await db.commit()
        __logger.debug(__l("Deleted component [component_id={0}]", component_id))


async def delete_component_symbol_relation(
    db: AsyncSession, component_id: int, symbol_id: int
):
    __logger.debug(
        __l(
            "Deleting component symbol relation[component_id={0}, symbol_id={1}]",
            component_id,
            symbol_id,
        )
    )

    await db.execute(
        delete(component_library_asc_table).where(
            component_library_asc_table.c.component_id == component_id,
            component_library_asc_table.c.library_ref_id == symbol_id,
        )
    )
    await db.commit()
    __logger.debug(
        __l(
            "Deleted component symbol relation [component_id={0}, symbol_id={1}]",
            component_id,
            symbol_id,
        )
    )


async def delete_component_footprint_relation(
    db: AsyncSession, component_id: int, footprint_id: int
):
    __logger.debug(
        __l(
            "Deleting component footprint relation[component_id={0}, footprint_id={1}]",
            component_id,
            footprint_id,
        )
    )

    await db.execute(
        delete(component_footprint_asc_table).where(
            component_footprint_asc_table.c.component_id == component_id,
            component_footprint_asc_table.c.footprint_ref_id == footprint_id,
        )
    )
    await db.commit()
    __logger.debug(
        __l(
            "Deleted component footprint relation [component_id={0}, footprint_id={1}]",
            component_id,
            footprint_id,
        )
    )
