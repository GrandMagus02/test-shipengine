from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ResidentialIndicator(str, Enum):
    UNKNOWN = "unknown"
    YES = "yes"
    NO = "no"


class AddressBase(BaseModel):
    name: Annotated[str, Field(examples=["Margie McMiller"])]
    address_line1: Annotated[str, Field(examples=["3800 North Lamar"])]
    address_line2: Annotated[str | None, Field(examples=["Suite 200"], default=None)] = None
    address_line3: Annotated[str | None, Field(examples=[None], default=None)] = None
    city_locality: Annotated[str, Field(examples=["Austin"])]
    state_province: Annotated[str, Field(examples=["TX"])]
    postal_code: Annotated[int, Field(examples=[78652])]
    address_residential_indicator: Annotated[ResidentialIndicator, Field(examples=[ResidentialIndicator.UNKNOWN])] = (
        ResidentialIndicator.UNKNOWN
    )


class Address(AddressBase):
    id: Annotated[int, Field(examples=[1])]
    country_code: Annotated[str, Field(examples=["US"])]


class AddressRead(AddressBase):
    pass


class AddressReadInternal(AddressBase):
    id: Annotated[int, Field(examples=[1])]

    email: Annotated[str, Field(examples=["email@example.com"])]
    phone: Annotated[str, Field(examples=["1234567890"])]
    company_name: Annotated[str | None, Field(examples=[None], default=None)] = None
    country_code: Annotated[str, Field(examples=["US"])]


class AddressCreate(AddressBase):
    model_config = ConfigDict(extra="forbid")

    email: Annotated[str, Field(examples=["email@example.com"])]
    phone: Annotated[str, Field(examples=["1234567890"])]
    company_name: Annotated[str | None, Field(examples=["Company Name"], default=None)] = None
    country_code: Annotated[str, Field(examples=["US"])]


class AddressUpdate(AddressBase):
    model_config = ConfigDict(extra="forbid")

    id: Annotated[int, Field(examples=[1])]
    country_code: Annotated[str | None, Field(examples=["US"], default=None)]


class AddressUpdateInternal(AddressUpdate):
    updated_at: datetime


class AddressDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: Annotated[int, Field(examples=[1])]
    is_deleted: bool
    deleted_at: datetime
