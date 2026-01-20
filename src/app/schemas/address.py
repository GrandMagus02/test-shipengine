from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class AddressBase(BaseModel):
    name: Annotated[str, Field(examples=["Margie McMiller"])]
    address_line1: Annotated[str, Field(examples=["3800 North Lamar"])]
    address_line2: Annotated[str, Field(examples=["Suite 200"])]
    city_locality: Annotated[str, Field(examples=["Austin"])]
    state_province: Annotated[str, Field(examples=["TX"])]
    postal_code: Annotated[int, Field(examples=[78652])]
    address_residential_indicator: Annotated[str, Field(examples=["unknown"])] = "unknown"


class Address(AddressBase):
    id: Annotated[int, Field(examples=[1])]
    country_code: Annotated[str, Field(examples=["US"])]


class AddressRead(AddressBase):
    pass


class AddressReadDetailed(AddressBase):
    id: Annotated[int, Field(examples=[1])]
    country_code: Annotated[str, Field(examples=["US"])]


class AddressCreate(AddressBase):
    model_config = ConfigDict(extra="forbid")
    pass


class AddressUpdate(AddressBase):
    model_config = ConfigDict(extra="forbid")

    id: Annotated[int, Field(examples=[1])]
    country_code: Annotated[str | None, Field(examples=["US"], default=None)]


class AddressDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: Annotated[int, Field(examples=[1])]
    is_deleted: bool
    deleted_at: datetime
