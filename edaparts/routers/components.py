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

from fastapi import APIRouter, Depends, Query, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import edaparts.services.component_service
from dtos.components_dtos import (
    map_component_model_to_query_dto,
    ComponentsListResultDto,
    ComponentUpdateRequestDto,
)
from edaparts.dtos.components_dtos import (
    ComponentCreateRequestDto,
    ComponentSpecificQueryDto,
)
from edaparts.services.database import get_db
from edaparts.services.exceptions import ApiError

router = APIRouter(prefix="/components", tags=["components"])


@router.post("")
async def create_component(
    body: ComponentCreateRequestDto, db: AsyncSession = Depends(get_db)
) -> ComponentSpecificQueryDto:
    try:
        mapped_model = body.component.to_model()
        component = await edaparts.services.component_service.create_component(
            db, mapped_model
        )
        return map_component_model_to_query_dto(component)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.put("/{component_id}")
async def update_component(
    component_id: int,
    body: ComponentUpdateRequestDto,
    db: AsyncSession = Depends(get_db),
) -> ComponentSpecificQueryDto:
    try:
        mapped_model = body.component.to_model()
        component = await edaparts.services.component_service.update_component(
            db, component_id, mapped_model
        )
        return map_component_model_to_query_dto(component)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.get("")
async def list_components(
    page_n: Annotated[int | None, Query(gt=0)] = 1,
    page_size: Annotated[int | None, Query(gt=0)] = 20,
    db: AsyncSession = Depends(get_db),
) -> ComponentsListResultDto:
    try:
        results, total_count = (
            await edaparts.services.component_service.get_component_list(
                db, page_n, page_size
            )
        )
        return ComponentsListResultDto(
            page_size=page_size,
            page_number=page_n,
            total_elements=total_count,
            elements=[map_component_model_to_query_dto(m) for m in results],
        )
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.get("/{component_id}")
async def get_component(
    component_id: int, db: AsyncSession = Depends(get_db)
) -> ComponentSpecificQueryDto:
    try:
        result = await edaparts.services.component_service.get_component(
            db, component_id
        )
        return map_component_model_to_query_dto(result)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.delete("/{component_id}", status_code=204, response_class=Response)
async def delete_component(
    component_id: int, db: AsyncSession = Depends(get_db)
) -> None:
    try:
        await edaparts.services.component_service.delete_component(db, component_id)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )
