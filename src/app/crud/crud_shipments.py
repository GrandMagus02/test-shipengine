from typing import Any

from fastcrud import FastCRUD, JoinConfig, aliased
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.address import Address
from ..models.shipment import Shipment
from ..models.warehouse import Warehouse
from ..schemas.address import AddressRead
from ..schemas.shipment import (
    ShipmentCreateInternal,
    ShipmentDelete,
    ShipmentRead,
    ShipmentReadDetailed,
    ShipmentUpdate,
    ShipmentUpdateInternal,
)
from ..schemas.warehouse import WarehouseRead


class CRUDShipment(
    FastCRUD[
        Shipment,
        ShipmentCreateInternal,
        ShipmentUpdate,
        ShipmentUpdateInternal,
        ShipmentDelete,
        ShipmentRead,
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
        Get multiple shipments with joined warehouse, ship_to, and ship_from addresses.
        """
        warehouse_alias = aliased(Warehouse, name="warehouse")
        ship_to_alias = aliased(Address, name="ship_to")
        ship_from_alias = aliased(Address, name="ship_from")

        return await self.get_multi_joined(
            db=db,
            schema_to_select=ShipmentReadDetailed,
            limit=limit,
            offset=offset,
            is_deleted=False,
            joins_config=[
                JoinConfig(
                    model=warehouse_alias,
                    join_on=Shipment.warehouse_id == warehouse_alias.id,
                    join_prefix="warehouse",
                    schema_to_select=WarehouseRead,
                    join_type="left",
                ),
                JoinConfig(
                    model=ship_to_alias,
                    join_on=Shipment.ship_to_id == ship_to_alias.id,
                    join_prefix="ship_to",
                    schema_to_select=AddressRead,
                    join_type="left",
                ),
                JoinConfig(
                    model=ship_from_alias,
                    join_on=Shipment.ship_from_id == ship_from_alias.id,
                    join_prefix="ship_from",
                    schema_to_select=AddressRead,
                    join_type="left",
                ),
            ],
            nested_schema_to_select={
                "warehouse": WarehouseRead,
                "ship_to": AddressRead,
                "ship_from": AddressRead,
            },
            nest_joins=True,
            **kwargs,
        )

    async def get_detailed(
        self,
        db: AsyncSession,
        id: int,
        **kwargs: Any,
    ) -> ShipmentReadDetailed | None:
        """
        Get a single shipment with joined warehouse, ship_to, and ship_from addresses.
        """
        warehouse_alias = aliased(Warehouse, name="warehouse")
        ship_to_alias = aliased(Address, name="ship_to")
        ship_from_alias = aliased(Address, name="ship_from")

        return await self.get_joined(
            db=db,
            id=id,
            is_deleted=False,
            schema_to_select=ShipmentReadDetailed,
            joins_config=[
                JoinConfig(
                    model=warehouse_alias,
                    join_on=Shipment.warehouse_id == warehouse_alias.id,
                    join_prefix="warehouse",
                    schema_to_select=WarehouseRead,
                    join_type="left",
                ),
                JoinConfig(
                    model=ship_to_alias,
                    join_on=Shipment.ship_to_id == ship_to_alias.id,
                    join_prefix="ship_to",
                    schema_to_select=AddressRead,
                    join_type="left",
                ),
                JoinConfig(
                    model=ship_from_alias,
                    join_on=Shipment.ship_from_id == ship_from_alias.id,
                    join_prefix="ship_from",
                    schema_to_select=AddressRead,
                    join_type="left",
                ),
            ],
            nest_joins=True,
            **kwargs,
        )


crud_shipments = CRUDShipment(Shipment)
