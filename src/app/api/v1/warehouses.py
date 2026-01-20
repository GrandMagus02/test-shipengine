from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.database import async_get_db
from app.core.exceptions.http_exceptions import NotFoundException
from app.crud.crud_warehouses import crud_warehouses
from app.schemas.warehouse import WarehouseCreate, WarehouseRead, WarehouseUpdate
from app.services.service_warehouses import service_warehouses

router = APIRouter(tags=["warehouses"], prefix="/warehouses")


@router.get("", response_model=list[WarehouseRead], description="List all warehouses")
async def list_warehouses(
    request: Request,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> list[WarehouseRead]:
    warehouses_data = await crud_warehouses.get_multi(
        db=db,
        limit=None,  # all
        is_deleted=False,
        schema_to_select=WarehouseRead,
    )
    return warehouses_data.values()


@router.post("", response_class=Response, status_code=201, description="Create a new warehouse")
async def create_warehouse(
    request: Request,
    warehouse: WarehouseCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Response:
    await service_warehouses.create_warehouse(
        db=db,
        warehouse=warehouse,
        schema_to_select=WarehouseRead,
    )
    return Response(status_code=201)


@router.get("/{warehouse_id}", response_model=WarehouseRead, description="Get a warehouse by ID")
async def read_warehouse(
    request: Request,
    warehouse_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> WarehouseRead:
    warehouse_data = await crud_warehouses.get(
        db=db,
        id=warehouse_id,
        is_deleted=False,
        schema_to_select=WarehouseRead,
    )
    if warehouse_data is None:
        raise NotFoundException("Warehouse not found")
    return warehouse_data


@router.put("/{warehouse_id}", response_class=Response, description="Update a warehouse")
async def update_warehouse(
    request: Request,
    warehouse_id: int,
    warehouse: WarehouseUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Response:
    await crud_warehouses.update(
        db=db,
        id=warehouse_id,
        object=warehouse,
        schema_to_select=WarehouseRead,
    )
    return Response(status_code=200)


@router.delete("/{warehouse_id}", response_class=Response, description="Delete a warehouse")
async def delete_warehouse(
    request: Request,
    warehouse_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Response:
    await crud_warehouses.delete(
        db=db,
        id=warehouse_id,
        schema_to_select=WarehouseRead,
    )
    return Response(status_code=200)
