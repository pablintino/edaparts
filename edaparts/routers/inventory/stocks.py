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
