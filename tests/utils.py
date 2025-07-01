from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import date

from src.usholidays.countryholidays.models import Holiday, HolidayState, State
from src.usholidays.core.models import HolidayTypeEnum
from src.usholidays.core.utils import us_states


async def populate_test_db(session: AsyncSession):
    test_holiday = Holiday(
        name="Testing National Day",
        date=date(2025, 3, 12),
        custom=False,
        type=HolidayTypeEnum.national,
    )
    for current_state in us_states:
        test_holiday.states.append(HolidayState(state=State(name=current_state)))
    session.add(test_holiday)
    await session.flush()

    test_holiday = Holiday(
        name="Testing Local Day",
        date=date(2025, 10, 10),
        custom=True,
        type=HolidayTypeEnum.local,
    )

    append_state = ["CA", "AL"]
    for state_name in append_state:
        test_state = await session.scalar(select(State).filter_by(name=state_name))
        test_holiday.states.append(HolidayState(state=test_state))
    session.add(test_holiday)

    await session.commit()
