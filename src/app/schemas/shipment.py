from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas import TimestampSchema
from ..schemas.address import AddressCreate, AddressRead
from ..schemas.warehouse import WarehouseRead


class ShipmentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TrackingUpdateStatusType(str, Enum):
    NOT_FOUND = "not_found"
    NO_TRACKING = "no_tracking"
    TERMINAL = "terminal"
    UPDATED = "updated"
    ERROR = "error"


class ShipmentBase(BaseModel):
    warehouse_id: Annotated[int, Field(examples=[1])]
    carrier: Annotated[str | None, Field(examples=["usps"], default=None)] = None
    service_code: Annotated[str | None, Field(examples=["usps_priority"], default=None)] = None
    tracking_number: Annotated[str | None, Field(examples=["9400111899223197428490"], default=None)] = None
    status: Annotated[ShipmentStatus | None, Field(examples=[ShipmentStatus.PENDING], default=None)] = None


class Shipment(ShipmentBase, TimestampSchema):
    id: Annotated[int, Field(examples=[1])]
    ship_to_id: Annotated[int, Field(examples=[1])]
    ship_from_id: Annotated[int, Field(examples=[2])]


class ShipmentRead(ShipmentBase):
    id: Annotated[int, Field(examples=[1])]
    ship_to_id: Annotated[int, Field(examples=[1])]
    ship_from_id: Annotated[int, Field(examples=[2])]
    created_at: datetime


class ShipmentReadDetailed(ShipmentRead):
    warehouse: WarehouseRead
    ship_to: AddressRead
    ship_from: AddressRead


class ShipmentCreate(ShipmentBase):
    model_config = ConfigDict(extra="forbid")

    ship_to: AddressCreate
    ship_from: AddressCreate


class ShipmentCreateInternal(ShipmentBase):
    model_config = ConfigDict(extra="forbid")

    ship_to_id: Annotated[int, Field(examples=[1])]
    ship_from_id: Annotated[int, Field(examples=[2])]


class ShipmentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    warehouse_id: Annotated[int, Field(examples=[1])] | None = None
    carrier: Annotated[str | None, Field(examples=["usps"], default=None)] = None
    service_code: Annotated[str | None, Field(examples=["usps_priority"], default=None)] = None
    tracking_number: Annotated[str | None, Field(examples=["9400111899223197428490"], default=None)] = None
    status: Annotated[ShipmentStatus | None, Field(examples=[ShipmentStatus.PENDING], default=None)] = None
    ship_to: AddressCreate | None = None
    ship_from: AddressCreate | None = None


class ShipmentUpdateInternal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    warehouse_id: Annotated[int, Field(examples=[1])] | None = None
    ship_to_id: Annotated[int, Field(examples=[1])] | None = None
    ship_from_id: Annotated[int, Field(examples=[2])] | None = None
    carrier: Annotated[str | None, Field(examples=["usps"], default=None)] = None
    service_code: Annotated[str | None, Field(examples=["usps_priority"], default=None)] = None
    tracking_number: Annotated[str | None, Field(examples=["9400111899223197428490"], default=None)] = None
    status: Annotated[ShipmentStatus | None, Field(examples=[ShipmentStatus.PENDING], default=None)] = None
    updated_at: datetime


class ShipmentDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime


class ShipmentRestoreDeleted(BaseModel):
    is_deleted: bool


class ShipmentTrackingUpdateResponse(BaseModel):
    message: Annotated[str, Field(description="Response message")]
    shipment_id: Annotated[int, Field(description="ID of the shipment", examples=[1])]
    job_enqueued: Annotated[bool, Field(description="Whether the tracking update job was successfully enqueued")]
    job_id: Annotated[
        str | None, Field(description="ARQ job ID if job was enqueued", default=None, examples=["abc123"])
    ] = None


class TrackingUpdateStatus(BaseModel):
    status: Annotated[
        TrackingUpdateStatusType,
        Field(
            description="Status of the tracking update operation",
            examples=[TrackingUpdateStatusType.NOT_FOUND, TrackingUpdateStatusType.UPDATED],
        ),
    ]
    shipment_id: Annotated[int, Field(description="ID of the shipment", examples=[1])]
    current_status: Annotated[
        str | None,
        Field(
            description="Current status of the shipment (used for terminal state responses)",
            examples=["delivered"],
            default=None,
        ),
    ] = None
    old_status: Annotated[
        str | None,
        Field(
            description="Previous status of the shipment (used for updated responses)",
            examples=["pending"],
            default=None,
        ),
    ] = None
    new_status: Annotated[
        str | None,
        Field(
            description="New status of the shipment (used for updated responses)",
            examples=["processing"],
            default=None,
        ),
    ] = None
    error: Annotated[
        str | None,
        Field(
            description="Error message describing what went wrong (used for error responses)",
            examples=["Database connection failed"],
            default=None,
        ),
    ] = None
