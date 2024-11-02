from fastapi import APIRouter

import edaparts.routers.inventory.locations
import edaparts.routers.inventory.items
import edaparts.routers.inventory.categories
import edaparts.routers.inventory.stocks

router = APIRouter(prefix="/inventory", tags=["inventory"])
router.include_router(edaparts.routers.inventory.locations.router)
router.include_router(edaparts.routers.inventory.items.router)
router.include_router(edaparts.routers.inventory.categories.router)
router.include_router(edaparts.routers.inventory.stocks.router)
