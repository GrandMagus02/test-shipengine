from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.schemas.shipment import ShipmentStatus

from ..core.db.database import Base

if TYPE_CHECKING:
    from ..models.address import Address
    from ..models.warehouse import Warehouse


class Shipment(Base):
    __tablename__ = "shipment"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouse.id"), index=True)
    ship_to_id: Mapped[int] = mapped_column(ForeignKey("address.id"), index=True)
    ship_from_id: Mapped[int] = mapped_column(ForeignKey("address.id"), index=True)

    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse",
        foreign_keys=[warehouse_id],
        lazy="selectin",
        init=False,
    )
    ship_to: Mapped["Address"] = relationship(
        "Address",
        foreign_keys=[ship_to_id],
        lazy="selectin",
        init=False,
    )
    ship_from: Mapped["Address"] = relationship(
        "Address",
        foreign_keys=[ship_from_id],
        lazy="selectin",
        init=False,
    )

    # Shipment-specific fields
    carrier: Mapped[str | None] = mapped_column(String(50), default=None)
    service_code: Mapped[str | None] = mapped_column(String(50), default=None)
    tracking_number: Mapped[str | None] = mapped_column(String(100), default=None, index=True)
    status: Mapped[ShipmentStatus | None] = mapped_column(Enum(ShipmentStatus), default=None, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
