from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.address import AddressRead


class WarehouseBase(BaseModel):
    name: Annotated[str, Field(examples=["Warehouse 1"])]
    is_default: Annotated[bool, Field(examples=[True])]
    created_at: Annotated[datetime, Field(examples=[datetime.now()])]


class Warehouse(WarehouseBase):
    id: Annotated[int, Field(examples=[1])]
    origin_address_id: Annotated[int, Field(examples=[1])]
    return_address_id: Annotated[int, Field(examples=[2])]


class WarehouseRead(BaseModel):
    origin_address: AddressRead
    return_address: AddressRead


class WarehouseCreate(WarehouseBase):
    model_config = ConfigDict(extra="forbid")


class WarehouseCreateInternal(WarehouseCreate):
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
