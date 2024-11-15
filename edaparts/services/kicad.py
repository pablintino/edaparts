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

from edaparts.models.components.component_model import ComponentModel
from edaparts.models.internal.kicad_models import KiCadPart, KiCadPartProperty
from edaparts.services.exceptions import ApiError, ResourceNotFoundApiError
from edaparts.utils.helpers import BraceMessage as __l
from edaparts.models import LibraryReference
from edaparts.models.internal.internal_models import CadType

__logger = logging.getLogger(__name__)


def __generate_components_types_dict() -> typing.Dict[typing.Type[ComponentModel], str]:
    components_list = [
        alchemy_info.entity
        for alchemy_info in inspect(ComponentModel).polymorphic_map.values()
        if alchemy_info.entity != ComponentModel
    ]
    result = {}
    for component in components_list:
        name = component.__name__.replace("Model", "")
        matches = re.finditer(
            ".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", name
        )

        result[component] = " ".join([m.group(0) for m in matches])
    return {k: v for k, v in sorted(result.items(), key=lambda item: item[1])}


def get_components_categories() -> list[str]:
    return list(__components_types_dict.values())


async def get_components_for_category(
    db: AsyncSession, category_id: int
) -> typing.Sequence[ComponentModel]:
    if category_id >= len(__components_types_dict):
        raise ApiError(
            f"Invalid category. ID cannot be greater than {len(__components_types_dict) -1}"
        )
    __logger.debug(__l("Listing components for [category_id={0}]", category_id))

    model = list(__components_types_dict.keys())[category_id]
    query = (
        select(model)
        .join(ComponentModel.library_ref)
        .where(LibraryReference.cad_type == CadType.KICAD)
        .order_by(ComponentModel.id.desc())
    )
    result_page = await db.scalars(query)

    return result_page.fetchall()


async def get_component(db: AsyncSession, component_id: int) -> KiCadPart:
    component = (
        await db.scalars(
            select(ComponentModel)
            .join(ComponentModel.library_ref)
            .filter(
                ComponentModel.id == component_id,
                LibraryReference.cad_type == CadType.KICAD,
            )
            .options(selectinload(ComponentModel.footprint_refs))
            .options(selectinload(ComponentModel.library_ref))
            .limit(1)
        )
    ).first()
    if not component:
        raise ResourceNotFoundApiError("Component not found", missing_id=component_id)

    symbol_ref = f"{component.library_ref.alias}:{component.library_ref.reference}"
    properties = __compute_component_properties(component)
    part = KiCadPart(
        id=component.id,
        name=component.mpn,
        symbolIdStr=symbol_ref,
        fields=properties,
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
