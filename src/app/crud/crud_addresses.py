from fastcrud import FastCRUD

from ..models.address import Address
from ..schemas.address import (
    AddressCreate,
    AddressDelete,
    AddressRead,
    AddressUpdate,
    AddressUpdateInternal,
)


class CRUDAddress(
    FastCRUD[
        Address,
        AddressCreate,
        AddressUpdate,
        AddressUpdateInternal,
        AddressDelete,
        AddressRead,
    ]
):
    pass


crud_addresses = CRUDAddress(Address)
