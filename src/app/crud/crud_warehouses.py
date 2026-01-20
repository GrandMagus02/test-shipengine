from fastcrud import FastCRUD

from ..models.warehouse import Warehouse
from ..schemas.warehouse import (
    WarehouseCreateInternal,
    WarehouseDelete,
    WarehouseRead,
    WarehouseUpdate,
    WarehouseUpdateInternal,
)


class CRUDWarehouse(
    FastCRUD[
        Warehouse,
        WarehouseCreateInternal,
        WarehouseUpdate,
        WarehouseUpdateInternal,
        WarehouseDelete,
        WarehouseRead,
    ]
):
    pass


crud_warehouses = CRUDWarehouse(Warehouse)
