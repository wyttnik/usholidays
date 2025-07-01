from fastapi import APIRouter, Depends, status, Query
from fastapi_filter import FilterDepends

from datetime import date
from typing import Annotated, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from countryholidays.schemas import (
    HolidayCreateSchema,
    HolidaySchema,
    HolidayUpdateSchema,
)
from countryholidays.services import (
    get_holidays_service,
    create_holiday_service,
    update_holiday_by_id_service,
    delete_holiday_by_id_service,
)
from core.dependencies import get_async_session
from countryholidays.utils import HolidayFilter
from auth.models import User
from auth.fastapi_users import current_active_user

router = APIRouter(tags=["Holidays"], prefix="/holidays")


@router.get("", response_model=list[HolidaySchema])
async def get_holidays(
    holiday_filter: Annotated[HolidayFilter, FilterDepends(HolidayFilter)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    year: Annotated[
        Optional[str], Query(max_length=4, min_length=4, pattern="^\\d+$")
    ] = None,
    month: Annotated[
        Optional[str], Query(max_length=2, min_length=2, pattern="^\\d+$")
    ] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    holidays = await get_holidays_service(
        session=session,
        apiFilter=holiday_filter,
        year=year,
        month=month,
        start=start_date,
        end=end_date,
    )

    return holidays


@router.post("", response_model=HolidaySchema, status_code=status.HTTP_201_CREATED)
async def create_holiday(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[User, Depends(current_active_user)],
    holiday_in: HolidayCreateSchema,
):
    holiday_created = await create_holiday_service(session, holiday_in)
    return holiday_created


@router.put("/{id}", response_model=HolidaySchema)
async def update_holiday_by_id(
    id: int,
    new_holiday: HolidayUpdateSchema,
    _: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    updated_holiday = await update_holiday_by_id_service(session, id, new_holiday)
    return updated_holiday


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holiday_by_id(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[User, Depends(current_active_user)],
    id: int,
):
    await delete_holiday_by_id_service(session, id)
