from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from src.usholidays.countryholidays.models import Holiday, HolidayState
from src.usholidays.core.models import HolidayTypeEnum
from src.usholidays.countryholidays.utils import HolidayFilter
from src.usholidays.countryholidays.services import (
    get_holidays_service,
    create_holiday_service,
    update_holiday_by_id_service,
    delete_holiday_by_id_service,
)
from src.usholidays.countryholidays.schemas import (
    HolidaySchema,
    HolidayCreateSchema,
    HolidayUpdateSchema,
)

from httpx import AsyncClient
from fastapi import HTTPException, status

# from contextlib import nullcontext
import pytest
import json
from datetime import date


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize(
    "year, month, start, end, case",
    [
        ("2025", "10", None, None, 1),
        (None, None, date(2025, 1, 1), date(2025, 5, 20), 2),
        (
            "2025",
            None,
            date(2025, 10, 1),
            date(2025, 12, 20),
            3,
        ),
        (None, None, None, None, 4),
    ],
)
async def test_get_holidays_service(
    client: AsyncClient,
    db_session: AsyncSession,
    year: str,
    month: str,
    start: date,
    end: date,
    case: int,
):
    try:
        holiday_list: list[Holiday] = await get_holidays_service(
            session=db_session,
            apiFilter=HolidayFilter(),
            year=year,
            month=month,
            start=start,
            end=end,
        )
        match case:
            case 1:
                assert len(holiday_list) == 1

                holiday = holiday_list[0]

                assert HolidaySchema.model_validate(
                    holiday
                ).model_dump_json() == json.dumps(
                    {
                        "name": "Testing Local Day",
                        "date": "2025-10-10",
                        "states": ["AL", "CA"],
                    },
                    separators=(",", ":"),
                )

            case 2:
                assert len(holiday_list) == 1

                holiday = holiday_list[0]
                assert holiday.name == "Testing National Day"
                assert holiday.date == date(2025, 3, 12)

            case 4:
                assert len(holiday_list) == 2

                assert holiday_list[0].name == "Testing National Day"
                assert holiday_list[1].name == "Testing Local Day"

    except HTTPException as e:
        match case:
            case 3:
                assert e.status_code == status.HTTP_404_NOT_FOUND
                assert e.detail == "Wrong path parameters"


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize(
    "holiday, case",
    [
        (
            HolidayCreateSchema(
                name="Testing Day1", date=date(2025, 1, 1), states=["CA"]
            ),
            1,
        ),
        (
            HolidayCreateSchema(
                name="Testing Day2", date=date(2025, 12, 1), states=["OO"]
            ),
            2,
        ),
        (
            HolidayCreateSchema(
                name="Testing National Day", date=date(2025, 12, 1), states=["NY"]
            ),
            3,
        ),
    ],
)
async def test_create_holiday_service(
    db_session: AsyncSession, holiday: HolidayCreateSchema, case: int
):
    try:
        created_holiday = await create_holiday_service(
            session=db_session, holiday_in=holiday
        )

        assert created_holiday.type == HolidayTypeEnum.local

        db_holiday = await db_session.scalar(
            select(Holiday)
            .filter_by(name=holiday.name)
            .options(selectinload(Holiday.states).joinedload(HolidayState.state))
        )

        assert db_holiday is not None
        assert db_holiday.name == created_holiday.name

        await db_session.delete(db_holiday)
        await db_session.commit()
        # await delete_holiday_by_id_service(db_session, db_holiday.id)

    except HTTPException as e:
        match case:
            case 2:
                assert e.status_code == status.HTTP_404_NOT_FOUND
                assert e.detail == "No such state exists in database"

            case 3:
                assert e.status_code == status.HTTP_409_CONFLICT
                assert (
                    e.detail
                    == f"Holiday with the name: {holiday.name} already exists in database"
                )


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize(
    "new_holiday, case",
    [
        (
            HolidayUpdateSchema(
                name="Testing Day 1", date=date(2025, 1, 1), states=["OK"]
            ),
            1,
        ),
        (
            HolidayUpdateSchema(
                name="Testing Day 2", date=date(2025, 12, 2), states=["OO"]
            ),
            2,
        ),
        (
            HolidayUpdateSchema(
                name="Testing Day 3", date=date(2025, 12, 3), states=["NY"]
            ),
            3,
        ),
        (
            HolidayUpdateSchema(
                name="Testing Day 4", date=date(2025, 12, 4), states=["NY"]
            ),
            4,
        ),
    ],
)
async def test_update_holiday_by_id_service(
    db_session: AsyncSession, new_holiday: HolidayUpdateSchema, case: int
):
    match case:
        case 1 | 2:
            id = case

        case 3:
            id = 2

        case _:
            id = 200

    try:
        await update_holiday_by_id_service(db_session, id, new_holiday)

        updated_holiday = await db_session.scalar(
            select(Holiday)
            .filter_by(id=id)
            .options(selectinload(Holiday.states).joinedload(HolidayState.state))
        )

        assert updated_holiday is not None
        assert updated_holiday.name == new_holiday.name
        assert [hst.state.name for hst in updated_holiday.states] == new_holiday.states

    except HTTPException as e:
        match case:
            case 1:
                assert e.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
                assert (
                    e.detail
                    == f"Holiday with id {id} is not custom. You can change or delete holidays only downloaded by users"
                )

            case 2:
                assert e.status_code == status.HTTP_404_NOT_FOUND
                assert e.detail == "No such state exists in database"

            case 4:
                assert e.status_code == status.HTTP_404_NOT_FOUND
                assert e.detail == f"Holiday with id {id} was not found"


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize(
    "case",
    [
        (1),
        (2),
        (3),
    ],
)
async def test_delete_holiday_by_id_service(db_session: AsyncSession, case: int):
    match case:
        case 1 | 2:
            id = case

        case _:
            id = 200
    try:
        await delete_holiday_by_id_service(db_session, id)

        deleted_holiday = await db_session.scalar(select(Holiday).filter_by(id=id))
        assert deleted_holiday is None

    except HTTPException as e:
        match case:
            case 1:
                assert e.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
                assert (
                    e.detail
                    == f"Holiday with id {id} is not custom. You can change or delete holidays only downloaded by users"
                )

            case 3:
                assert e.status_code == status.HTTP_404_NOT_FOUND
                assert e.detail == f"Holiday with id {id} was not found"
