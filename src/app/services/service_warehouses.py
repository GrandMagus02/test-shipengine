from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_addresses import crud_addresses
from app.crud.crud_warehouses import crud_warehouses
from app.schemas.warehouse import Warehouse, WarehouseCreate, WarehouseCreateInternal

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


service_warehouses = WarehouseService()
