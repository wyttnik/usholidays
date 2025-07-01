from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from datetime import date

from countryholidays.schemas import (
    HolidayCreateSchema,
    HolidayUpdateSchema,
)
from countryholidays.utils import (
    HolidayFilter,
    get_holiday_by_id,
    get_query_between_dates,
    get_query_by_year_month,
    get_states_by_names,
)
from countryholidays.models import Holiday, HolidayState, State
from core.models.base import HolidayTypeEnum


async def get_holidays_service(
    session: AsyncSession,
    apiFilter: HolidayFilter,
    year: str | None = None,
    month: str | None = None,
    start: date | None = None,
    end: date | None = None,
) -> list[Holiday]:
    """
    Запрос может включать только год и месяц, либо только период,
    либо ничего из первых вариантов. Дополнительные фильтры будут
    применены к любому из вышеперечисленных вариантов. В последнем
    случае фильтрация произойдёт по всей таблице
    """
    stmt = select(Holiday).outerjoin(HolidayState).outerjoin(State)
    option = (
        (0 if year is None else 1) * 1000
        + (0 if month is None else 1) * 100
        + (0 if start is None else 1) * 10
        + (0 if end is None else 1)
    )
    # год и месяц
    if option // 100 == 11 and option % 100 == 0:
        stmt = apiFilter.filter(
            get_query_by_year_month(stmt, int(year), int(month)).options(  # type: ignore
                selectinload(Holiday.states).joinedload(HolidayState.state)
            )
        )
    # старт и конец периода
    elif option % 100 == 11 and option // 100 == 0:
        stmt = apiFilter.filter(
            get_query_between_dates(stmt, start, end).options(  # type: ignore
                selectinload(Holiday.states).joinedload(HolidayState.state)
            )
        )
    # не был задан год и месяц либо период
    elif option == 0:
        stmt = apiFilter.filter(
            stmt.options(selectinload(Holiday.states).joinedload(HolidayState.state))
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wrong path parameters"
        )
    result = await session.execute(stmt)
    holiday_list = result.scalars().unique().all()
    return list(holiday_list)


async def create_holiday_service(
    session: AsyncSession, holiday_in: HolidayCreateSchema
) -> Holiday:
    db_holiday_result = await session.execute(
        select(Holiday).filter_by(name=holiday_in.name)
    )
    holiday = db_holiday_result.scalar()

    if holiday is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Holiday with the name: {holiday_in.name} already exists in database",
        )

    holiday = Holiday(name=holiday_in.name, date=holiday_in.date, custom=True)
    holiday.type = (
        HolidayTypeEnum.national
        if len(holiday_in.states) == 50
        else HolidayTypeEnum.local
    )

    db_states = await get_states_by_names(session, holiday_in.states)

    for state in db_states:
        holiday.states.append(HolidayState(state=state))

    session.add(holiday)
    await session.commit()
    return holiday


async def update_holiday_by_id_service(
    session: AsyncSession,
    id: int,
    new_holiday: HolidayUpdateSchema,
) -> Holiday:
    db_holiday = await get_holiday_by_id(need_join=True, id=id, session=session)

    db_holiday.name = new_holiday.name
    db_holiday.date = new_holiday.date
    db_holiday.states.clear()

    db_states = await get_states_by_names(session, new_holiday.states)

    for state in db_states:
        db_holiday.states.append(HolidayState(state=state))

    session.add(db_holiday)
    await session.commit()
    return db_holiday


async def delete_holiday_by_id_service(session: AsyncSession, id: int):
    db_holiday = await get_holiday_by_id(need_join=False, id=id, session=session)

    await session.delete(db_holiday)
    await session.commit()
