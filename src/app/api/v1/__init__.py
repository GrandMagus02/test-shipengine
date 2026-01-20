from fastapi import APIRouter

from .warehouses import router as warehouses_router

router = APIRouter(prefix="/v1")
router.include_router(warehouses_router)
