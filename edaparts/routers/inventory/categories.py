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

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

import edaparts.services.inventory_service
from edaparts.dtos.components_dtos import map_component_model_to_query_dto
from edaparts.dtos.inventory_dtos import (
    InventoryCategoryCreateUpdateRequestDto,
    InventoryCategoryQueryDto,
    InventoryCategoriesQueryDto,
    InventoryCategoryReferenceCreationUpdateDto,
    InventoryItemQueryDto,
    InventoryItemsQueryDto,
)
from edaparts.services.database import get_db

router = APIRouter(prefix="/categories", tags=["inventory", "categories"])


@router.post("")
async def create_category(
    body: InventoryCategoryCreateUpdateRequestDto, db: AsyncSession = Depends(get_db)
) -> InventoryCategoryQueryDto:
    category = await edaparts.services.inventory_service.create_category(
        db, body.name, description=body.description
    )
    return InventoryCategoryQueryDto.from_model(category)


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    body: InventoryCategoryCreateUpdateRequestDto,
    db: AsyncSession = Depends(get_db),
) -> InventoryCategoryQueryDto:
    category = await edaparts.services.inventory_service.update_category(
        db, category_id, body.name, description=body.description
    )
    return InventoryCategoryQueryDto.from_model(category)


@router.get("/{category_id}")
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
) -> InventoryCategoryQueryDto:
    category = await edaparts.services.inventory_service.get_category(db, category_id)
    return InventoryCategoryQueryDto.from_model(category)


@router.post("/{category_id}/parent")
async def set_parent_category(
    body: InventoryCategoryReferenceCreationUpdateDto,
    category_id: int,
    db: AsyncSession = Depends(get_db),
) -> InventoryCategoryQueryDto:
    category = await edaparts.services.inventory_service.set_category_parent(
        db, category_id, body.category_id
    )
    return InventoryCategoryQueryDto.from_model(category)


@router.delete("/{category_id}/parent", status_code=204, response_class=Response)
async def delete_parent_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    await edaparts.services.inventory_service.remove_category_parent(db, category_id)


@router.get("")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    page_n: Annotated[int | None, Query(gt=0)] = 1,
    page_size: Annotated[int | None, Query(gt=0)] = 20,
    only_root: bool | None = False,
) -> InventoryCategoriesQueryDto:
    categories, total_count = await edaparts.services.inventory_service.get_categories(
        db, page_n, page_size, only_root=only_root
    )
    return InventoryCategoriesQueryDto(
        page_size=page_size,
        page_number=page_n,
        total_elements=total_count,
        elements=[InventoryCategoryQueryDto.from_model(m) for m in categories],
    )


@router.get("/{category_id}/items")
async def list_category_items(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    page_n: Annotated[int | None, Query(gt=0)] = 1,
    page_size: Annotated[int | None, Query(gt=0)] = 20,
    include_component: bool | None = False,
) -> InventoryItemsQueryDto:
    results, total_count = await edaparts.services.inventory_service.get_category_items(
        db, category_id, page_n, page_size, load_component=include_component
    )
    dtos = [
        InventoryItemQueryDto.from_model(
            item_model,
            component_dto=(
                map_component_model_to_query_dto(item_model.component)
                if include_component and item_model.component
                else None
            ),
        )
        for item_model in results
    ]
    page_dto = InventoryItemsQueryDto(
        page_size=page_size,
        page_number=page_n,
        total_elements=total_count,
        elements=dtos,
    )
    return page_dto
