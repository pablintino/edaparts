from fastapi import APIRouter
import edaparts.routers.inventory.inventory
import edaparts.routers.components
import edaparts.routers.symbols

router = APIRouter()
router.include_router(edaparts.routers.inventory.inventory.router)
router.include_router(edaparts.routers.components.router)
router.include_router(edaparts.routers.symbols.router)
