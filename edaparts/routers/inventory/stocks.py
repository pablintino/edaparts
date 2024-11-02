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


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import edaparts.services.inventory_service
from edaparts.dtos.inventory_dtos import (
    InventoryMassStockMovementDto,
    InventoryMassStockMovementQueryDto,
)
from edaparts.services.database import get_db
from edaparts.services.exceptions import ApiError

router = APIRouter(prefix="/stocks", tags=["inventory", "stocks"])


@router.post("/updates", tags=["inventory", "locations"])
async def stock_mass_update(
    body: InventoryMassStockMovementDto, db: AsyncSession = Depends(get_db)
) -> InventoryMassStockMovementQueryDto:
    try:
        update_results = await edaparts.services.inventory_service.stock_mass_update(
            db, InventoryMassStockMovementDto.to_model(body)
        )
        return InventoryMassStockMovementQueryDto.from_model(update_results)
    except ApiError as error:
        # todo temporal simple handling of the exceptions
        raise HTTPException(
            status_code=error.http_code, detail=error.details or error.msg
        )
