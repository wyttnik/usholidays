from sqlalchemy.orm import Mapped, relationship, mapped_column

from typing import TYPE_CHECKING, List

from core.models import Base

if TYPE_CHECKING:
    from countryholidays.models import HolidayState


class State(Base):
    __tablename__ = "states"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    holidays: Mapped[List["HolidayState"]] = relationship(
        back_populates="state",
        # secondary="holidays_states",
        cascade="all, delete-orphan",
    )
