from datetime import UTC, datetime
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.http_exceptions import NotFoundException
from app.crud.crud_addresses import crud_addresses
from app.crud.crud_warehouses import crud_warehouses
from app.schemas.warehouse import (
    Warehouse,
    WarehouseCreate,
    WarehouseCreateInternal,
    WarehouseUpdate,
    WarehouseUpdateInternal,
)

T = TypeVar("T", bound=BaseModel)


class WarehouseService:
    @staticmethod
    async def create_warehouse(
        db: AsyncSession,
        warehouse: WarehouseCreate,
        schema_to_select: type[T] = Warehouse,
    ) -> T:
        async with db.begin():
            origin_address = await crud_addresses.create(
                db=db,
                object=warehouse.origin_address,
                commit=False,
            )

            if warehouse.return_address is not None:
                # TODO: double check business logic - do we need to create a new row for the return address?
                return_address = await crud_addresses.create(
                    db=db,
                    object=warehouse.return_address,
                    commit=False,
                )
            else:
                return_address = origin_address

            warehouse_create = WarehouseCreateInternal(
                name=warehouse.name,
                is_default=warehouse.is_default,
                origin_address_id=origin_address.id,
                return_address_id=return_address.id,
            )

            result = await crud_warehouses.create(
                db=db,
                object=warehouse_create,
                schema_to_select=schema_to_select,
                commit=False,
            )

            return result

    @staticmethod
    async def update_warehouse(
        db: AsyncSession,
        warehouse_id: int,
        warehouse: WarehouseUpdate,
    ) -> None:
        async with db.begin():
            current_warehouse = await crud_warehouses.get(
                db=db,
                id=warehouse_id,
                schema_to_select=Warehouse,
            )
            if current_warehouse is None:
                raise NotFoundException("Warehouse not found")

            # Handle both dict and Pydantic model instances
            if isinstance(current_warehouse, dict):
                origin_address_id = current_warehouse["origin_address_id"]
                return_address_id = current_warehouse["return_address_id"]
            else:
                origin_address_id = current_warehouse.origin_address_id
                return_address_id = current_warehouse.return_address_id

            if warehouse.origin_address is not None:
                origin_address = await crud_addresses.create(
                    db=db,
                    object=warehouse.origin_address,
                    commit=False,
                )
                origin_address_id = origin_address.id

            if warehouse.return_address is not None:
                return_address = await crud_addresses.create(
                    db=db,
                    object=warehouse.return_address,
                    commit=False,
                )
                return_address_id = return_address.id

            warehouse_update = WarehouseUpdateInternal(
                name=warehouse.name,
                is_default=warehouse.is_default,
                origin_address_id=origin_address_id,
                return_address_id=return_address_id,
                updated_at=datetime.now(UTC),
            )

            await crud_warehouses.update(
                db=db,
                id=warehouse_id,
                object=warehouse_update,
                commit=False,
            )


service_warehouses = WarehouseService()
