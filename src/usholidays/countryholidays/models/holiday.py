from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import Boolean, String

from datetime import date
from typing import TYPE_CHECKING, List

from core.models import Base, HolidayTypeEnum

if TYPE_CHECKING:
    from countryholidays.models import HolidayState


class Holiday(Base):
    __tablename__ = "holidays"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    date: Mapped[date]
    custom: Mapped[bool] = mapped_column(Boolean, default=False, server_default="False")
    type: Mapped["HolidayTypeEnum"] = mapped_column(String)

    states: Mapped[List["HolidayState"]] = relationship(
        back_populates="holiday",
        # secondary="holidays_states",
        cascade="all, delete-orphan",
    )
