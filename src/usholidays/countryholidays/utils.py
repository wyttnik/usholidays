from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter

from fastapi import HTTPException, status
from typing import Optional
from datetime import date
import re

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, Select, and_, extract

from countryholidays.models import State, Holiday, HolidayState
from core.models import HolidayTypeEnum
from core.utils import (
    get_national_holidays_names,
    us_states,
    get_country_holidays_by_state,
)


class StateFilter(Filter):
    name: Optional[str] = None
    name__in: Optional[list[str]] = None

    class Constants(Filter.Constants):
        model = State


class HolidayFilter(Filter):
    name: Optional[str] = None
    custom: Optional[bool] = None
    type: Optional[HolidayTypeEnum] = None
    states: Optional[StateFilter] = FilterDepends(with_prefix("state", StateFilter))

    class Constants(Filter.Constants):
        model = Holiday


def get_query_by_year_month(stmt: Select, year: int, month: int):
    return stmt.where(
        and_(
            extract("YEAR", Holiday.date) == year,
            extract("MONTH", Holiday.date) == month,
        )
    )


def get_query_between_dates(stmt: Select, start: date, end: date):
    return stmt.where(Holiday.date.between(start, end))


def create_holiday_with_model_type(holiday_name: str, holiday_date: date) -> Holiday:
    holiday_type = (
        HolidayTypeEnum.national
        if holiday_name in get_national_holidays_names()
        else HolidayTypeEnum.local
    )
    return Holiday(name=holiday_name, date=holiday_date, type=holiday_type)


async def get_holiday_by_id(
    need_join: bool,
    id: int,
    session: AsyncSession,
) -> Holiday:
    stmt = select(Holiday).filter_by(id=id)

    if need_join:
        stmt = stmt.options(selectinload(Holiday.states).joinedload(HolidayState.state))

    db_holiday = await session.scalar(stmt)

    if db_holiday is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holiday with id {id} was not found",
        )

    if not db_holiday.custom:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"Holiday with id {id} is not custom. You can change or delete holidays only downloaded by users",
        )

    return db_holiday


async def get_states_by_names(session: AsyncSession, states: list[str]):
    db_states_result = await session.execute(
        select(State).filter(State.name.in_(states))
    )
    db_states = db_states_result.scalars().all()
    if len(db_states) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such state exists in database",
        )

    return db_states


async def populate_db(session: AsyncSession):
    table_exists = await session.execute(select(1).select_from(Holiday).limit(1))
    if table_exists.scalar():
        return

    delimiters = r"[&/;]"
    holidays_list: dict[str, dict[str, Holiday]] = {}

    for state_name in us_states:
        state_model = State(name=state_name)

        for holiday_date, holiday_name in get_country_holidays_by_state(
            state_name
        ).items():
            """
            Иногда могут попадаться названия вроде Martin King & St. Jeff Day
            это два разных праздника, но могут отмечаться в один день в штате,
            поэтому их надо разделить
            """
            holidays_by_date = [i.strip() for i in re.split(delimiters, holiday_name)]

            for cur_holiday_name in holidays_by_date:
                holiday_list_by_name = holidays_list.get(cur_holiday_name)
                if holiday_list_by_name is None:
                    holiday_model = create_holiday_with_model_type(
                        cur_holiday_name, holiday_date
                    )
                    holidays_list[cur_holiday_name] = {str(holiday_date): holiday_model}
                    holiday_state_model = HolidayState(holiday=holiday_model)
                else:
                    holiday_by_date = holiday_list_by_name.get(str(holiday_date))
                    if holiday_by_date is None:
                        holiday_model = create_holiday_with_model_type(
                            cur_holiday_name, holiday_date
                        )
                        holidays_list[cur_holiday_name][str(holiday_date)] = (
                            holiday_model
                        )
                        holiday_state_model = HolidayState(holiday=holiday_model)
                    else:
                        holiday_state_model = HolidayState(holiday=holiday_by_date)

                state_model.holidays.append(holiday_state_model)
        session.add(state_model)
    await session.commit()
