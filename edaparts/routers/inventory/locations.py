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

import edaparts.services.inventory_service
from edaparts.dtos.inventory_dtos import (
    InventoryLocationsQueryDto,
    InventoryLocationQueryDto,
    InventoryLocationCreateDto,
)
from edaparts.services.database import get_db

router = APIRouter()


@router.post("/locations", tags=["inventory", "locations"])
async def create_location(
    body: InventoryLocationCreateDto, db: AsyncSession = Depends(get_db)
) -> InventoryLocationQueryDto:
    location = await edaparts.services.inventory_service.create_location(
        db, body.name, description=body.description
    )
    return InventoryLocationQueryDto.from_model(location)


@router.get("/locations", tags=["inventory", "locations"])
async def list_locations(
    page_n: Annotated[int | None, Query(gt=0)] = 1,
    page_size: Annotated[int | None, Query(gt=0)] = 20,
    db: AsyncSession = Depends(get_db),
) -> InventoryLocationsQueryDto:
    results, total_count = await edaparts.services.inventory_service.get_locations(
        db, page_n, page_size
    )
    return InventoryLocationsQueryDto(
        page_size=page_size,
        page_number=page_n,
        total_elements=total_count,
        elements=[InventoryLocationQueryDto.from_model(m) for m in results],
    )


@router.delete(
    "/locations/{location_id}",
    tags=["inventory", "locations"],
    status_code=204,
    response_class=Response,
)
async def delete_location(location_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await edaparts.services.inventory_service.delete_stock_location(db, location_id)


@router.get("/locations/{location_id}", tags=["inventory", "locations"])
async def get_location(
    location_id: int, db: AsyncSession = Depends(get_db)
) -> InventoryLocationQueryDto:
    result = await edaparts.services.inventory_service.get_location(db, location_id)
    return InventoryLocationQueryDto.from_model(result)
