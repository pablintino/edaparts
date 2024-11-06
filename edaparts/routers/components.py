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
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

import edaparts.services.component_service
from edaparts.dtos.symbols_dtos import SymbolQueryDto
from edaparts.dtos.components_dtos import (
    ComponentCreateRequestDto,
    ComponentSpecificQueryDto,
    ComponentsListResultDto,
    ComponentUpdateRequestDto,
    map_component_model_to_query_dto,
)
from edaparts.dtos.footprints_dtos import (
    FootprintsComponentReferenceDto,
    FootprintQueryDto,
)
from edaparts.services.database import get_db

router = APIRouter(prefix="/components", tags=["components"])


@router.post("")
async def create_component(
    body: ComponentCreateRequestDto, db: AsyncSession = Depends(get_db)
) -> ComponentSpecificQueryDto:
    mapped_model = body.component.to_model()
    component = await edaparts.services.component_service.create_component(
        db, mapped_model
    )
    return map_component_model_to_query_dto(component)


@router.put("/{component_id}")
async def update_component(
    component_id: int,
    body: ComponentUpdateRequestDto,
    db: AsyncSession = Depends(get_db),
) -> ComponentSpecificQueryDto:
    mapped_model = body.component.to_model()
    component = await edaparts.services.component_service.update_component(
        db, component_id, mapped_model
    )
    return map_component_model_to_query_dto(component)


@router.get("")
async def list_components(
    page_n: Annotated[int | None, Query(gt=0)] = 1,
    page_size: Annotated[int | None, Query(gt=0)] = 20,
    db: AsyncSession = Depends(get_db),
) -> ComponentsListResultDto:
    results, total_count = await edaparts.services.component_service.get_component_list(
        db, page_n, page_size
    )
    return ComponentsListResultDto(
        page_size=page_size,
        page_number=page_n,
        total_elements=total_count,
        elements=[map_component_model_to_query_dto(m) for m in results],
    )


@router.get("/{component_id}")
async def get_component(
    component_id: int, db: AsyncSession = Depends(get_db)
) -> ComponentSpecificQueryDto:
    result = await edaparts.services.component_service.get_component(db, component_id)
    return map_component_model_to_query_dto(result)


@router.delete("/{component_id}", status_code=204, response_class=Response)
async def delete_component(
    component_id: int, db: AsyncSession = Depends(get_db)
) -> None:
    await edaparts.services.component_service.delete_component(db, component_id)


@router.post("/{component_id}/footprints")
async def create_footprints_relations(
    component_id: int,
    body: FootprintsComponentReferenceDto,
    db: AsyncSession = Depends(get_db),
) -> FootprintsComponentReferenceDto:
    footprints_ids = (
        await edaparts.services.component_service.create_footprints_relation(
            db, component_id, body.footprint_ids
        )
    )
    return FootprintsComponentReferenceDto(footprint_ids=footprints_ids)


@router.delete(
    "/{component_id}/footprints/{footprint_id}",
    status_code=204,
    response_class=Response,
)
async def delete_footprints_relations(
    component_id: int, footprint_id: int, db: AsyncSession = Depends(get_db)
) -> None:
    await edaparts.services.component_service.delete_component_footprint_relation(
        db, component_id, footprint_id
    )


@router.get("/{component_id}/footprints")
async def list_component_footprints(
    component_id: int, db: AsyncSession = Depends(get_db)
) -> list[FootprintQueryDto]:

    footprint_models = (
        await edaparts.services.component_service.get_component_footprint_relations(
            db, component_id
        )
    )
    return [FootprintQueryDto.from_model(model) for model in footprint_models]


@router.post(
    "/{component_id}/symbol/{symbol_id}", status_code=204, response_class=Response
)
async def create_symbol_relation(
    component_id: int, symbol_id: int, db: AsyncSession = Depends(get_db)
) -> None:
    await edaparts.services.component_service.create_symbol_relation(
        db, component_id, symbol_id
    )


@router.get("/{component_id}/symbol")
async def create_symbol_relation(
    component_id: int, db: AsyncSession = Depends(get_db)
) -> SymbolQueryDto:
    symbol_model = (
        await edaparts.services.component_service.get_component_symbol_relation(
            db, component_id
        )
    )
    return SymbolQueryDto.from_model(symbol_model)


@router.delete("/{component_id}/symbol", status_code=204, response_class=Response)
async def delete_symbol_relation(
    component_id: int, db: AsyncSession = Depends(get_db)
) -> None:
    await edaparts.services.component_service.delete_component_symbol_relation(
        db, component_id
    )
