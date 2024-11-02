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

from sqlalchemy import select, func, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, selectinload

from edaparts.models.components import ComponentModelType
from edaparts.models.components.component_model import ComponentModel
from edaparts.models.libraries.footprint_reference_model import FootprintReference
from edaparts.models.libraries.library_reference_model import LibraryReference
from edaparts.services import inventory_service
from edaparts.services.exceptions import (
    ResourceAlreadyExistsApiError,
    ResourceNotFoundApiError,
    RelationAlreadyExistsError,
    InvalidComponentFieldsError,
    RelationExistsError,
)
from edaparts.utils.helpers import BraceMessage as __l

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


def update_create_symbol_relation(component_id, symbol_id, is_update=False):
    __logger.debug(
        __l(
            "Creating new component-symbol relation [component_id={0}, symbol_id={1}]",
            component_id,
            symbol_id,
        )
    )
    component = ComponentModel.query.get(component_id)
    if component:
        library_ref = LibraryReference.query.get(symbol_id)
        if library_ref is not None:
            #  Just protect against false updates from bad POST usage
            if not is_update and component.library_ref_id:
                raise RelationAlreadyExistsError(
                    __l(
                        "Cannot create relation. Component already has a relation [component_id={0}, library_ref_id={1}]",
                        component_id,
                        component.library_ref_id,
                    )
                )

            component.library_ref = library_ref
            component.library_ref_id = symbol_id
            db.session.add(component)
            db.session.commit()
            __logger.debug(
                f'Component symbol {"updated" if is_update else "created"}.'
                f" Component {component_id} symbol {symbol_id}"
            )
            return component

        raise ResourceNotFoundApiError("Symbol not found", missing_id=symbol_id)

    raise ResourceNotFoundApiError("Component not found", missing_id=component_id)


def create_footprints_relation(component_id, footprint_ids):
    __logger.debug(
        __l(
            "Creating new component-footprint relation [component_id={0}, footprint_ids={1}]",
            component_id,
            footprint_ids,
        )
    )
    component = ComponentModel.query.get(component_id)
    footprint_refs = []

    # Verify that the component exists before trying anything else
    if not component:
        raise ResourceNotFoundApiError("Component not found", missing_id=component_id)

    # Add only the footprints that are not already associated
    footprints_to_add = [
        foot_id
        for foot_id in footprint_ids
        if foot_id not in [cfr.id for cfr in component.footprint_refs]
    ]

    for footprint_id in footprints_to_add:
        footprint_ref = FootprintReference.query.get(footprint_id)
        if footprint_ref:
            footprint_refs.append(footprint_ref)
            db.session.add(footprint_ref)
        else:
            raise ResourceNotFoundApiError(
                "Footprint not found", missing_id=footprint_id
            )

    component.footprint_refs.extend(footprint_refs)
    db.session.add(component)
    db.session.commit()
    __logger.debug(
        __l(
            "Component footprints updated [component_id={0}, footprint_ids={1}",
            component_id,
            footprint_ids,
        )
    )
    return [ref.id for ref in component.footprint_refs]


def get_component_symbol_relation(component_id):
    __logger.debug(
        __l("Querying symbol relation for component [component_id={0}]", component_id)
    )
    component = ComponentModel.query.get(component_id)
    if not component:
        raise ResourceNotFoundApiError("Component not found", missing_id=component_id)

    return component.library_ref


def get_component_footprint_relations(component_id, complete_footprints=False):
    __logger.debug(
        __l(
            "Querying footprint relations for component [component_id={0}]",
            component_id,
        )
    )
    component = ComponentModel.query.get(component_id)
    if component:
        result_list = []
        if complete_footprints:
            result_list = list(component.footprint_refs)
        else:
            for footprint in component.footprint_refs:
                result_list.append(footprint.id)
        return result_list

    raise ResourceNotFoundApiError("Component not found", missing_id=component_id)


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
    result_page = await db.execute(query)
    total_count = await db.scalar(select(func.count()).select_from(ComponentModel))
    return result_page.scalars().all(), total_count


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


def delete_component_symbol_relation(component_id):
    __logger.debug(
        __l("Deleting component symbol relation[component_id={0}]", component_id)
    )
    component = ComponentModel.query.get(component_id)
    if not component:
        raise ResourceNotFoundApiError("Component not found", missing_id=component_id)
    symbol_id = component.library_ref_id
    component.library_ref_id = Nones
    component.library_ref = None
    db.session.add(component)
    db.session.commit()
    __logger.debug(
        __l(
            "Deleted component symbol relation [component_id={0}, symbol_id={1}]",
            component_id,
            symbol_id,
        )
    )


def delete_component_footprint_relation(component_id, footprint_id):
    __logger.debug(
        __l(
            "Deleting component footprint relation[component_id={0}, footprint_id={1}]",
            component_id,
            footprint_id,
        )
    )
    component = ComponentModel.query.get(component_id)
    if not component:
        raise ResourceNotFoundApiError("Component not found", missing_id=component_id)

    component.footprint_refs = [
        x for x in component.footprint_refs if x.id != footprint_id
    ]
    db.session.add(component)
    db.session.commit()
    __logger.debug(
        __l(
            "Deleted component footprint relation [component_id={0}, footprint_id={1}]",
            component_id,
            footprint_id,
        )
    )
