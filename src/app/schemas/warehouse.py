from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.core.schemas import TimestampSchema
from app.schemas.address import AddressCreate, AddressRead


class WarehouseBase(BaseModel):
    name: Annotated[str, Field(examples=["Warehouse 1"])]
    is_default: Annotated[bool, Field(examples=[True])] = False


class Warehouse(WarehouseBase, TimestampSchema):
    id: Annotated[int, Field(examples=[1])]
    origin_address_id: Annotated[int, Field(examples=[1])]
    return_address_id: Annotated[int, Field(examples=[2])]


class WarehouseRead(BaseModel):
    origin_address: AddressRead
    return_address: AddressRead
    created_at: datetime


class WarehouseCreate(WarehouseBase):
    model_config = ConfigDict(extra="forbid")

    origin_address: AddressCreate
    return_address: AddressCreate | None = None


class WarehouseCreateInternal(WarehouseBase):
    model_config = ConfigDict(extra="forbid")

    origin_address_id: Annotated[int, Field(examples=[1])]
    return_address_id: Annotated[int, Field(examples=[2])]


class WarehouseUpdate(WarehouseBase):
    model_config = ConfigDict(extra="forbid")


class WarehouseUpdateInternal(WarehouseUpdate):
    updated_at: datetime


class WarehouseDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime


class WarehouseRestoreDeleted(BaseModel):
    is_deleted: bool
