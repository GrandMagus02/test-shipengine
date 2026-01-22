from typing import Any

from fastcrud import FastCRUD, JoinConfig, aliased
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.address import Address
from ..models.warehouse import Warehouse
from ..schemas.address import AddressRead
from ..schemas.warehouse import (
    WarehouseCreateInternal,
    WarehouseDelete,
    WarehouseRead,
    WarehouseReadDetailed,
    WarehouseUpdate,
    WarehouseUpdateInternal,
)


class CRUDWarehouse(
    FastCRUD[
        Warehouse,
        WarehouseCreateInternal,
        WarehouseUpdate,
        WarehouseUpdateInternal,
        WarehouseDelete,
        WarehouseRead,
    ]
):
    async def get_multi_detailed(
        self,
        db: AsyncSession,
        offset: int = 0,
        limit: int | None = 100,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get multiple warehouses with joined origin and return addresses.
        """
        origin_address_alias = aliased(Address, name="origin_address")
        return_address_alias = aliased(Address, name="return_address")

        return await self.get_multi_joined(
            db=db,
            schema_to_select=WarehouseReadDetailed,
            limit=limit,
            offset=offset,
            is_deleted=False,
            joins_config=[
                JoinConfig(
                    model=origin_address_alias,
                    join_on=Warehouse.origin_address_id == origin_address_alias.id,
                    join_prefix="origin_address",
                    schema_to_select=AddressRead,
                    join_type="left",
                ),
                JoinConfig(
                    model=return_address_alias,
                    join_on=Warehouse.return_address_id == return_address_alias.id,
                    join_prefix="return_address",
                    schema_to_select=AddressRead,
                    join_type="left",
                ),
            ],
            nested_schema_to_select={
                "origin_address": AddressRead,
                "return_address": AddressRead,
            },
            nest_joins=True,
            **kwargs,
        )

    async def get_detailed(
        self,
        db: AsyncSession,
        id: int,
        **kwargs: Any,
    ) -> WarehouseReadDetailed | None:
        """
        Get a single warehouse with joined origin and return addresses.
        """
        origin_address_alias = aliased(Address, name="origin_address")
        return_address_alias = aliased(Address, name="return_address")

        return await self.get_joined(
            db=db,
            id=id,
            is_deleted=False,
            schema_to_select=WarehouseReadDetailed,
            joins_config=[
                JoinConfig(
                    model=origin_address_alias,
                    join_on=Warehouse.origin_address_id == origin_address_alias.id,
                    join_prefix="origin_address",
                    schema_to_select=AddressRead,
                    join_type="left",
                ),
                JoinConfig(
                    model=return_address_alias,
                    join_on=Warehouse.return_address_id == return_address_alias.id,
                    join_prefix="return_address",
                    schema_to_select=AddressRead,
                    join_type="left",
                ),
            ],
            nest_joins=True,
            **kwargs,
        )


crud_warehouses = CRUDWarehouse(Warehouse)
