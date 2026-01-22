from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions.http_exceptions import NotFoundException
from ..core.utils import queue
from ..crud.crud_addresses import crud_addresses
from ..crud.crud_shipments import crud_shipments
from ..crud.crud_warehouses import crud_warehouses
from ..schemas.shipment import (
    Shipment,
    ShipmentCreate,
    ShipmentCreateInternal,
    ShipmentUpdate,
    ShipmentUpdateInternal,
)


class ShipmentService:
    @staticmethod
    async def create_shipment(
        db: AsyncSession,
        shipment: ShipmentCreate,
    ):
        async with db.begin():
            warehouse = await crud_warehouses.get(
                db=db,
                id=shipment.warehouse_id,
            )
            if warehouse is None:
                raise NotFoundException("Warehouse not found")

            ship_to_address = await crud_addresses.create(
                db=db,
                object=shipment.ship_to,
                commit=False,
            )

            ship_from_address = await crud_addresses.create(
                db=db,
                object=shipment.ship_from,
                commit=False,
            )

            shipment_create = ShipmentCreateInternal(
                warehouse_id=shipment.warehouse_id,
                ship_to_id=ship_to_address.id,
                ship_from_id=ship_from_address.id,
                carrier=shipment.carrier,
                service_code=shipment.service_code,
                tracking_number=shipment.tracking_number,
                status=shipment.status,
            )

            result = await crud_shipments.create(
                db=db,
                object=shipment_create,
                commit=False,
            )

            if shipment.tracking_number and queue.pool is not None:
                shipment_id = result.id

                await queue.pool.enqueue_job(
                    "update_shipment_tracking_status",
                    shipment_id,
                    _defer_by=60,  # 1 minute
                )

            return result

    @staticmethod
    async def update_shipment(
        db: AsyncSession,
        shipment_id: int,
        shipment: ShipmentUpdate,
    ) -> None:
        async with db.begin():
            current_shipment: Shipment | None = await crud_shipments.get(
                db=db,
                id=shipment_id,
                schema_to_select=Shipment,
            )
            if current_shipment is None:
                raise NotFoundException("Shipment not found")

            ship_to_id = current_shipment.ship_to_id
            ship_from_id = current_shipment.ship_from_id

            if shipment.warehouse_id is not None:
                warehouse = await crud_warehouses.get(
                    db=db,
                    id=shipment.warehouse_id,
                )
                if warehouse is None:
                    raise NotFoundException("Warehouse not found")

            if shipment.ship_to is not None:
                ship_to_address = await crud_addresses.create(
                    db=db,
                    object=shipment.ship_to,
                    commit=False,
                )
                ship_to_id = ship_to_address.id

            if shipment.ship_from is not None:
                ship_from_address = await crud_addresses.create(
                    db=db,
                    object=shipment.ship_from,
                    commit=False,
                )
                ship_from_id = ship_from_address.id

            shipment_update = ShipmentUpdateInternal(
                warehouse_id=shipment.warehouse_id,
                ship_to_id=ship_to_id,
                ship_from_id=ship_from_id,
                carrier=shipment.carrier,
                service_code=shipment.service_code,
                tracking_number=shipment.tracking_number,
                status=shipment.status,
                updated_at=datetime.now(UTC),
            )

            await crud_shipments.update(
                db=db,
                id=shipment_id,
                object=shipment_update,
                commit=False,
            )

            tracking_number = shipment.tracking_number
            if tracking_number is None:
                tracking_number = current_shipment.tracking_number

            if tracking_number and queue.pool is not None:
                await queue.pool.enqueue_job(
                    "update_shipment_tracking_status",
                    shipment_id,
                    _defer_by=60,  # 1 minute
                )


service_shipments = ShipmentService()
