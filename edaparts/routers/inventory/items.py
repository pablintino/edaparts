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


import copy
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

import edaparts.services.inventory_service
from edaparts.dtos.components_dtos import map_component_model_to_query_dto
from edaparts.dtos.inventory_dtos import (
    InventoryItemQueryDto,
    InventoryItemsQueryDto,
    InventoryItemLocationStockQueryDto,
    InventoryItemPropertyQueryDto,
    InventoryItemPropertyUpdateDto,
    InventoryItemPropertyCreateRequestDto,
    InventoryItemCreateRequestDto,
    InventoryCategoryReferenceCreationUpdateDto,
    InventoryItemLocationReferenceDto,
    InventoryItemLocationStockUpdateResourceDto,
)
from edaparts.services import search_service
from edaparts.services.database import get_db

router = APIRouter(prefix="/items")


@router.post("", tags=["inventory", "items"])
async def create_item(
    body: InventoryItemCreateRequestDto, db: AsyncSession = Depends(get_db)
) -> InventoryItemQueryDto:
    item_model = await edaparts.services.inventory_service.create_standalone_item(
        db, InventoryItemCreateRequestDto.to_model(body)
    )
    return InventoryItemQueryDto.from_model(item_model)


@router.get("/{item_id}", tags=["inventory", "items"])
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    include_component: bool | None = False,
) -> InventoryItemQueryDto:
    result = await edaparts.services.inventory_service.get_item(
        db, item_id, load_component=include_component
    )
    return InventoryItemQueryDto.from_model(
        result,
        (
            map_component_model_to_query_dto(result.component)
            if include_component and result.component
            else None
        ),
    )


@router.delete(
    "/{item_id}",
    tags=["inventory", "items"],
    status_code=204,
    response_class=Response,
)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await edaparts.services.inventory_service.delete_item(db, item_id)


@router.get("", tags=["inventory", "items"])
async def list_items(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page_n: Annotated[int | None, Query(gt=0)] = 1,
    page_size: Annotated[int | None, Query(gt=0)] = 20,
    include_component: bool | None = False,
) -> InventoryItemsQueryDto:
    filters = copy.deepcopy(dict(request.query_params))
    filters.pop("page_n", None)
    filters.pop("page_size", None)
    filters.pop("include_component", None)
    results, total_count = await search_service.search_items(
        db, filters, page_n, page_size, load_component=include_component
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


@router.post("/{item_id}/properties", tags=["inventory", "items", "properties"])
async def create_item_property(
    item_id: int,
    body: InventoryItemPropertyCreateRequestDto,
    db: AsyncSession = Depends(get_db),
) -> InventoryItemPropertyQueryDto:
    item_model = await edaparts.services.inventory_service.add_property_to_item(
        db, item_id, InventoryItemPropertyCreateRequestDto.to_model(body)
    )
    return InventoryItemPropertyQueryDto.from_model(item_model)


@router.get("/{item_id}/properties", tags=["inventory", "items", "properties"])
async def list_item_properties(
    item_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[InventoryItemPropertyQueryDto]:
    item_properties = await edaparts.services.inventory_service.get_item_properties(
        db, item_id
    )
    return [
        InventoryItemPropertyQueryDto.from_model(model) for model in item_properties
    ]


@router.put(
    "/{item_id}/properties/{property_id}", tags=["inventory", "items", "properties"]
)
async def update_item_property(
    item_id: int,
    property_id: int,
    body: InventoryItemPropertyUpdateDto,
    db: AsyncSession = Depends(get_db),
) -> InventoryItemPropertyQueryDto:
    item_model = await edaparts.services.inventory_service.update_item_property(
        db, item_id, property_id, body.value
    )
    return InventoryItemPropertyQueryDto.from_model(item_model)


@router.delete(
    "/{item_id}/properties/{property_id}",
    tags=["inventory", "items", "properties"],
    status_code=204,
    response_class=Response,
)
async def delete_item_property(
    item_id: int,
    property_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    await edaparts.services.inventory_service.delete_item_property(
        db, item_id, property_id
    )


@router.post(
    "/{item_id}/category",
    tags=["inventory", "items", "categories"],
    status_code=204,
    response_class=Response,
)
async def set_item_category(
    item_id: int,
    body: InventoryCategoryReferenceCreationUpdateDto,
    db: AsyncSession = Depends(get_db),
) -> None:
    await edaparts.services.inventory_service.set_item_category(
        db, item_id, body.category_id
    )


@router.delete(
    "/{item_id}/category",
    tags=["inventory", "items", "categories"],
    status_code=204,
    response_class=Response,
)
async def delete_item_category(
    item_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    await edaparts.services.inventory_service.delete_item_category(db, item_id)


@router.post("/{item_id}/locations", tags=["inventory", "items", "locations"])
async def set_item_locations(
    item_id: int,
    body: InventoryItemLocationReferenceDto,
    db: AsyncSession = Depends(get_db),
) -> InventoryItemLocationReferenceDto:
    location_ids = (
        await edaparts.services.inventory_service.create_item_stocks_for_locations(
            db, item_id, body.location_ids
        )
    )
    return InventoryItemLocationReferenceDto(location_ids=location_ids)


@router.put(
    "/{item_id}/locations/{location_id}/stock", tags=["inventory", "items", "locations"]
)
async def update_stock_item_location(
    item_id: int,
    location_id: int,
    body: InventoryItemLocationStockUpdateResourceDto,
    db: AsyncSession = Depends(get_db),
) -> InventoryItemLocationStockQueryDto:
    item_location_stock = (
        await edaparts.services.inventory_service.update_item_location_stock_levels(
            db,
            item_id,
            location_id,
            min_stock_level=body.stock_min_level,
            min_notify_level=body.stock_notify_min_level,
        )
    )
    return InventoryItemLocationStockQueryDto.from_model(item_location_stock)


@router.get(
    "/{item_id}/locations/{location_id}/stock", tags=["inventory", "items", "locations"]
)
async def get_stock_item_location(
    item_id: int,
    location_id: int,
    db: AsyncSession = Depends(get_db),
) -> InventoryItemLocationStockQueryDto:
    item_location_stock = (
        await edaparts.services.inventory_service.get_item_stock_for_location(
            db,
            item_id,
            location_id,
        )
    )
    return InventoryItemLocationStockQueryDto.from_model(item_location_stock)
