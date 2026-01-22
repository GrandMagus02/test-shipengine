from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.db.database import Base

if TYPE_CHECKING:
    from ..models.address import Address


class Warehouse(Base):
    __tablename__ = "warehouse"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(50))
    origin_address_id: Mapped[int] = mapped_column(ForeignKey("address.id"), index=True)
    return_address_id: Mapped[int] = mapped_column(ForeignKey("address.id"), index=True)

    origin_address: Mapped["Address"] = relationship(
        "Address",
        foreign_keys=[origin_address_id],
        lazy="selectin",
        init=False,
    )
    return_address: Mapped["Address"] = relationship(
        "Address",
        foreign_keys=[return_address_id],
        lazy="selectin",
        init=False,
    )

    is_default: Mapped[bool] = mapped_column(default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
