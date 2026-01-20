from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(64))
    email: Mapped[str] = mapped_column(String(255))
    company_name: Mapped[str] = mapped_column(String(255))

    address_line1: Mapped[str] = mapped_column(String(255))
    address_line2: Mapped[str] = mapped_column(String(255))
    address_line3: Mapped[str] = mapped_column(String(255))

    city_locality: Mapped[str] = mapped_column(String(50))
    state_province: Mapped[str] = mapped_column(String(50))
    postal_code: Mapped[int] = mapped_column()

    country_code: Mapped[str] = mapped_column(String(2))
    address_residential_indicator: Mapped[str] = mapped_column(String(50), default="unknown")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
