import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

import structlog
import uvloop
from arq.worker import Worker

from ...core.db.database import local_session
from ...core.utils import queue
from ...crud.crud_shipments import crud_shipments
from ...schemas.shipment import (
    Shipment,
    ShipmentStatus,
    ShipmentUpdateInternal,
    TrackingUpdateStatus,
    TrackingUpdateStatusType,
)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def startup(ctx: Worker) -> None:
    logging.info("Worker Started")


async def shutdown(ctx: Worker) -> None:
    logging.info("Worker end")


async def on_job_start(ctx: dict[str, Any]) -> None:
    structlog.contextvars.bind_contextvars(job_id=ctx["job_id"])
    logging.info("Job Started")


async def on_job_end(ctx: dict[str, Any]) -> None:
    logging.info("Job Competed")
    structlog.contextvars.clear_contextvars()


def _get_mock_tracking_status(current_status: ShipmentStatus | None, tracking_number: str | None) -> ShipmentStatus:
    if not tracking_number:
        return ShipmentStatus.PENDING

    if current_status is None:
        return ShipmentStatus.PENDING

    status_progression = {
        ShipmentStatus.PENDING: ShipmentStatus.PROCESSING,
        ShipmentStatus.PROCESSING: ShipmentStatus.SHIPPED,
        ShipmentStatus.SHIPPED: ShipmentStatus.IN_TRANSIT,
        ShipmentStatus.IN_TRANSIT: ShipmentStatus.DELIVERED,
        ShipmentStatus.DELIVERED: ShipmentStatus.DELIVERED,  # Terminal state
        ShipmentStatus.CANCELLED: ShipmentStatus.CANCELLED,  # Terminal state
        ShipmentStatus.FAILED: ShipmentStatus.FAILED,  # Terminal state
    }

    return status_progression.get(current_status, ShipmentStatus.PENDING)


async def update_shipment_tracking_status(
    ctx: dict[str, Any],
    shipment_id: int,
) -> TrackingUpdateStatus:
    logging.info(f"Updating tracking status for shipment {shipment_id}")

    async with local_session() as db:
        try:
            shipment: Shipment | None = await crud_shipments.get(
                db=db,
                id=shipment_id,
                schema_to_select=Shipment,
            )

            if shipment is None:
                logging.warning(f"Shipment {shipment_id} not found")
                return TrackingUpdateStatus(
                    status=TrackingUpdateStatusType.NOT_FOUND,
                    shipment_id=shipment_id,
                )

            current_status = shipment.status
            tracking_number = shipment.tracking_number

            if not tracking_number:
                logging.info(f"Shipment {shipment_id} has no tracking number, skipping update")
                return TrackingUpdateStatus(
                    status=TrackingUpdateStatusType.NO_TRACKING,
                    shipment_id=shipment_id,
                )

            terminal_states = {
                ShipmentStatus.DELIVERED,
                ShipmentStatus.CANCELLED,
                ShipmentStatus.FAILED,
            }

            if current_status in terminal_states:
                logging.info(f"Shipment {shipment_id} is in terminal state {current_status}, no update needed")
                return TrackingUpdateStatus(
                    status=TrackingUpdateStatusType.TERMINAL,
                    shipment_id=shipment_id,
                    current_status=current_status.value,
                )

            new_status = _get_mock_tracking_status(current_status, tracking_number)

            shipment_update = ShipmentUpdateInternal(
                status=new_status,
                updated_at=datetime.now(UTC),
            )

            await crud_shipments.update(
                db=db,
                id=shipment_id,
                object=shipment_update,
                commit=True,
            )

            logging.info(f"Updated shipment {shipment_id} status from {current_status} to {new_status}")

            if new_status not in terminal_states and queue.pool is not None:
                await queue.pool.enqueue_job(
                    "update_shipment_tracking_status",
                    shipment_id,
                    _defer_by=300,  # 5 minutes
                )
                logging.info(f"Scheduled next tracking update for shipment {shipment_id} in 5 minutes")

            return TrackingUpdateStatus(
                status=TrackingUpdateStatusType.UPDATED,
                shipment_id=shipment_id,
                old_status=current_status.value if current_status else None,
                new_status=new_status.value,
            )

        except Exception as e:
            logging.error(f"Error updating tracking status for shipment {shipment_id}: {e}", exc_info=True)
            return TrackingUpdateStatus(
                status=TrackingUpdateStatusType.ERROR,
                shipment_id=shipment_id,
                error=str(e),
            )
