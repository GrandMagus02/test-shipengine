from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException
from ...crud.crud_warehouses import crud_warehouses
from ...schemas.warehouse import WarehouseCreate, WarehouseRead, WarehouseReadDetailed, WarehouseUpdate
from ...services.service_warehouses import service_warehouses

router = APIRouter(tags=["warehouses"], prefix="/warehouses")


@router.get(
    "",
    response_model=list[WarehouseReadDetailed],
    description="List all warehouses",
)
async def list_warehouses(
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[WarehouseReadDetailed]:
    result = await crud_warehouses.get_multi_detailed(
        db=db,
        limit=None,  # all
    )
    return result["data"]


@router.post(
    "",
    response_model=WarehouseRead,
    status_code=201,
    description="Create a new warehouse",
)
async def create_warehouse(
    warehouse: WarehouseCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> WarehouseRead:
    created = await service_warehouses.create_warehouse(
        db=db,
        warehouse=warehouse,
        schema_to_select=WarehouseRead,
    )
    return created


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseReadDetailed,
    description="Get a warehouse by ID",
)
async def read_warehouse(
    warehouse_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> WarehouseReadDetailed:
    warehouse = await crud_warehouses.get_detailed(
        db=db,
        id=warehouse_id,
    )
    if warehouse is None:
        raise NotFoundException("Warehouse not found")
    return warehouse


@router.put(
    "/{warehouse_id}",
    status_code=204,
    description="Update a warehouse",
)
async def update_warehouse(
    warehouse_id: int,
    warehouse: WarehouseUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> None:
    await service_warehouses.update_warehouse(
        db=db,
        warehouse_id=warehouse_id,
        warehouse=warehouse,
    )


@router.delete(
    "/{warehouse_id}",
    status_code=204,
    description="Delete a warehouse",
)
async def delete_warehouse(
    warehouse_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> None:
    await crud_warehouses.delete(
        db=db,
        id=warehouse_id,
        allow_multiple=False,
    )
