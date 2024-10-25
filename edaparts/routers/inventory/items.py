import copy
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

import edaparts.services.inventory_service

from edaparts.dtos.inventory_dtos import (
    InventoryItemQueryDto,
    InventoryItemsQueryDto,
    InventoryItemPropertyQueryDto,
    InventoryItemPropertyUpdateDto,
    InventoryItemPropertyCreateRequestDto,
    InventoryItemCreateRequestDto,
    InventoryCategoryReferenceCreationUpdateDto,
)
from edaparts.dtos.components_dtos import map_component_model_to_query_dto
from edaparts.services.database import get_db
from edaparts.services.exceptions import ApiError
from edaparts.services import search_service

router = APIRouter(prefix="/items")


@router.post("", tags=["inventory", "items"])
async def create_item(
    body: InventoryItemCreateRequestDto, db: AsyncSession = Depends(get_db)
) -> InventoryItemQueryDto:
    try:
        item_model = await edaparts.services.inventory_service.create_standalone_item(
            db, InventoryItemCreateRequestDto.to_model(body)
        )
        return InventoryItemQueryDto.from_model(item_model)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.get("/{item_id}", tags=["inventory", "items"])
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    include_component: bool | None = False,
) -> InventoryItemQueryDto:
    try:
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
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.delete(
    "/{item_id}",
    tags=["inventory", "items"],
    status_code=204,
    response_class=Response,
)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)) -> None:
    try:
        await edaparts.services.inventory_service.delete_item(db, item_id)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.get("", tags=["inventory", "items"])
async def list_items(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page_n: Annotated[int | None, Query(gt=0)] = 1,
    page_size: Annotated[int | None, Query(gt=0)] = 20,
    include_component: bool | None = False,
) -> InventoryItemsQueryDto:
    try:
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
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.post("/{item_id}/properties", tags=["inventory", "items", "properties"])
async def create_item_property(
    item_id: int,
    body: InventoryItemPropertyCreateRequestDto,
    db: AsyncSession = Depends(get_db),
) -> InventoryItemPropertyQueryDto:
    try:
        item_model = await edaparts.services.inventory_service.add_property_to_item(
            db, item_id, InventoryItemPropertyCreateRequestDto.to_model(body)
        )
        return InventoryItemPropertyQueryDto.from_model(item_model)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.get("/{item_id}/properties", tags=["inventory", "items", "properties"])
async def list_item_properties(
    item_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[InventoryItemPropertyQueryDto]:
    try:
        item_properties = await edaparts.services.inventory_service.get_item_properties(
            db, item_id
        )
        return [
            InventoryItemPropertyQueryDto.from_model(model) for model in item_properties
        ]
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.put(
    "/{item_id}/properties/{property_id}", tags=["inventory", "items", "properties"]
)
async def update_item_property(
    item_id: int,
    property_id: int,
    body: InventoryItemPropertyUpdateDto,
    db: AsyncSession = Depends(get_db),
) -> InventoryItemPropertyQueryDto:
    try:
        item_model = await edaparts.services.inventory_service.update_item_property(
            db, item_id, property_id, body.value
        )
        return InventoryItemPropertyQueryDto.from_model(item_model)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


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
    try:
        await edaparts.services.inventory_service.delete_item_property(
            db, item_id, property_id
        )
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
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
    try:
        await edaparts.services.inventory_service.set_item_category(
            db, item_id, body.category_id
        )
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
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
    try:
        await edaparts.services.inventory_service.delete_item_category(db, item_id)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )
