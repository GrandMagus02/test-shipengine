from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastcrud import PaginatedListResponse, compute_offset, paginated_response
from fastcrud.exceptions.http_exceptions import BadRequestException
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import NotFoundException, ServiceUnavailableException
from ...core.utils import queue
from ...crud.crud_shipments import crud_shipments
from ...schemas.shipment import (
    Shipment,
    ShipmentCreate,
    ShipmentRead,
    ShipmentReadDetailed,
    ShipmentUpdate,
)
from ...services.service_shipments import service_shipments

router = APIRouter(tags=["shipments"], prefix="/shipments")


@router.get(
    "",
    response_model=PaginatedListResponse[ShipmentReadDetailed],
    description="List all shipments",
)
async def list_shipments(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
) -> dict[str, Any]:
    shipments_data = await crud_shipments.get_multi_detailed(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
    )

    response: dict[str, Any] = paginated_response(crud_data=shipments_data, page=page, items_per_page=items_per_page)
    return response


@router.post(
    "",
    response_model=ShipmentRead,
    status_code=201,
    description="Create a new shipment",
)
async def create_shipment(
    shipment: ShipmentCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ShipmentRead:
    created = await service_shipments.create_shipment(
        db=db,
        shipment=shipment,
        schema_to_select=ShipmentRead,
    )
    return created


@router.get(
    "/{shipment_id}",
    response_model=ShipmentReadDetailed,
    description="Get a shipment by ID",
)
async def read_shipment(
    shipment_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> ShipmentReadDetailed:
    shipment = await crud_shipments.get_detailed(
        db=db,
        id=shipment_id,
    )
    if shipment is None:
        raise NotFoundException("Shipment not found")
    return shipment


@router.put(
    "/{shipment_id}",
    status_code=204,
    description="Update a shipment",
)
async def update_shipment(
    shipment_id: int,
    shipment: ShipmentUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> None:
    await service_shipments.update_shipment(
        db=db,
        shipment_id=shipment_id,
        shipment=shipment,
    )


@router.delete(
    "/{shipment_id}",
    status_code=204,
    description="Delete a shipment",
)
async def delete_shipment(
    shipment_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> None:
    await crud_shipments.delete(
        db=db,
        id=shipment_id,
    )


@router.post(
    "/{shipment_id}/update-tracking",
    status_code=204,
    description="Manually trigger a tracking status update for a shipment",
)
async def update_shipment_tracking(
    shipment_id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> None:
    shipment: Shipment | None = await crud_shipments.get(
        db=db,
        id=shipment_id,
        schema_to_select=Shipment,
    )
    if shipment is None:
        raise NotFoundException("Shipment not found")

    tracking_number = shipment.tracking_number
    if not tracking_number:
        raise BadRequestException("Shipment has no tracking number")

    if queue.pool is None:
        raise ServiceUnavailableException("Queue pool not available")

    await queue.pool.enqueue_job("update_shipment_tracking_status", shipment_id)
