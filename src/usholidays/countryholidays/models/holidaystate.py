from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import ForeignKey
from core.models import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from countryholidays.models import Holiday
    from countryholidays.models import State


class HolidayState(Base):
    __tablename__ = "holidays_states"
    holiday_id: Mapped[int] = mapped_column(
        ForeignKey(
            "holidays.id",
            # ondelete="CASCADE",
            # onupdate="cascade",
        ),
        primary_key=True,
    )
    state_id: Mapped[int] = mapped_column(
        ForeignKey(
            "states.id",
            # ondelete="CASCADE",
            # onupdate="cascade",
        ),
        primary_key=True,
    )

    holiday: Mapped["Holiday"] = relationship(back_populates="states")
    state: Mapped["State"] = relationship(back_populates="holidays")
