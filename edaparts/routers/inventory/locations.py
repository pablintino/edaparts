from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import edaparts.services.inventory_service
from edaparts.dtos.inventory_dtos import (
    InventoryLocationsQueryDto,
    InventoryLocationQueryDto,
    InventoryLocationCreateDto,
)
from edaparts.services.database import get_db
from edaparts.services.exceptions import ApiError

router = APIRouter()


@router.post("/locations", tags=["inventory", "locations"])
async def create_location(
    body: InventoryLocationCreateDto, db: AsyncSession = Depends(get_db)
) -> InventoryLocationQueryDto:
    try:
        location = await edaparts.services.inventory_service.create_location(
            db, body.name, description=body.description
        )
        return InventoryLocationQueryDto.from_model(location)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.get("/locations", tags=["inventory", "locations"])
async def list_locations(
    page_n: Annotated[int | None, Query(gt=0)] = 1,
    page_size: Annotated[int | None, Query(gt=0)] = 20,
    db: AsyncSession = Depends(get_db),
) -> InventoryLocationsQueryDto:
    try:
        results, total_count = await edaparts.services.inventory_service.get_locations(
            db, page_n, page_size
        )
        return InventoryLocationsQueryDto(
            page_size=page_size,
            page_number=page_n,
            total_elements=total_count,
            elements=[InventoryLocationQueryDto.from_model(m) for m in results],
        )
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.delete(
    "/locations/{location_id}",
    tags=["inventory", "locations"],
    status_code=204,
    response_class=Response,
)
async def delete_location(location_id: int, db: AsyncSession = Depends(get_db)) -> None:
    try:
        await edaparts.services.inventory_service.delete_stock_location(db, location_id)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )


@router.get("/locations/{location_id}", tags=["inventory", "locations"])
async def get_location(
    location_id: int, db: AsyncSession = Depends(get_db)
) -> InventoryLocationQueryDto:
    try:
        result = await edaparts.services.inventory_service.get_location(db, location_id)
        return InventoryLocationQueryDto.from_model(result)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )
