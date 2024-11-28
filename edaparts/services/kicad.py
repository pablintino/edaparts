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
import re
import typing

from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from edaparts.models import LibraryReference
from edaparts.models.components.component_model import ComponentModel
from edaparts.models.internal.internal_models import CadType
from edaparts.models.internal.kicad_models import (
    KiCadCategoryEntry,
    KiCadPart,
    KiCadPartProperty,
)
from edaparts.services.exceptions import ApiError, ResourceNotFoundApiError
from edaparts.utils.helpers import BraceMessage as __l

__logger = logging.getLogger(__name__)


def __generate_components_types_dict() -> typing.Dict[int, KiCadCategoryEntry]:
    components_list = [
        alchemy_info.entity
        for alchemy_info in inspect(ComponentModel).polymorphic_map.values()
        if alchemy_info.entity != ComponentModel
    ]
    result = {}
    for idx, component in enumerate(components_list):
        name = component.__name__.replace("Model", "")
        matches = re.finditer(
            ".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", name
        )
        # Avoid zero based indexes as IDs
        component_id = idx + 1
        result[component_id] = KiCadCategoryEntry(
            id=component_id,
            name=" ".join([m.group(0) for m in matches]),
            component_type=component,
        )
    return {k: v for k, v in sorted(result.items(), key=lambda item: item[1].name)}


def get_components_categories() -> typing.Dict[int, KiCadCategoryEntry]:
    return __components_types_dict


async def get_components_for_category(
    db: AsyncSession, category_id: int
) -> typing.Sequence[ComponentModel]:
    if category_id not in __components_types_dict:
        raise ResourceNotFoundApiError(
            f"Category {category_id} does not exist", missing_id=category_id
        )
    __logger.debug(__l("Listing components for [category_id={0}]", category_id))

    query = (
        select(__components_types_dict[category_id].component_type)
        .join(ComponentModel.library_refs)
        .where(LibraryReference.cad_type == CadType.KICAD)
        .order_by(ComponentModel.id.desc())
    )
    result_page = await db.scalars(query)

    return result_page.fetchall()


async def get_component(db: AsyncSession, component_id: int) -> KiCadPart:
    component = (
        await db.scalars(
            select(ComponentModel)
            .join(ComponentModel.library_refs)
            .filter(
                ComponentModel.id == component_id,
                LibraryReference.cad_type == CadType.KICAD,
            )
            .options(selectinload(ComponentModel.footprint_refs))
            .options(selectinload(ComponentModel.library_refs))
            .limit(1)
        )
    ).first()
    if not component:
        raise ResourceNotFoundApiError("Component not found", missing_id=component_id)

    if not component.library_refs:
        raise ApiError(
            f"Component {component_id} has no associated symbol", http_code=404
        )

    library_ref = component.library_refs[0]
    part = KiCadPart(
        id=component.id,
        name=component.mpn,
        symbolIdStr=f"{library_ref.alias}:{library_ref.reference}",
        fields=__compute_component_properties(component),
    )
    return part


def __compute_component_properties(
    component: ComponentModel,
) -> dict[str, KiCadPartProperty]:
    properties = {}
    to_discard_cols = ["id", "type", "comment_altium", "comment_kicad"]
    inspect_data = inspect(type(component))
    for key, relation in inspect_data.relationships.items():
        to_discard_cols.append(key)
        to_discard_cols.extend([rel_col.key for rel_col in relation.local_columns])
    for key, column_prop in inspect_data.mapper.column_attrs.items():
        if key in to_discard_cols:
            continue
        value = getattr(component, column_prop.key)
        if value is None:
            continue
        prop = key.replace("_", " ").title()
        properties[prop] = KiCadPartProperty(value=str(value), visible=False)
    if component.comment_kicad is not None:
        properties["Comment"] = KiCadPartProperty(
            value=component.comment_kicad, visible=True
        )

    # At the moment of writing this KiCad integration
    # it does not support comma/semicolon separated
    # footprints like in other integrations
    if component.footprint_refs:
        footprint_ref = next(iter(component.footprint_refs))
        properties["Footprint"] = KiCadPartProperty(
            value=f"{footprint_ref.alias}:{footprint_ref.reference}",
            visible=False,
        )
    return properties


__components_types_dict = __generate_components_types_dict()
