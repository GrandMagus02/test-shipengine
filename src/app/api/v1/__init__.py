from fastapi import APIRouter

from .shipments import router as shipments_router
from .warehouses import router as warehouses_router

router = APIRouter(prefix="/v1")
router.include_router(warehouses_router)
router.include_router(shipments_router)
