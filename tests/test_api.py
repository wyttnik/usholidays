from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.usholidays.countryholidays.models import Holiday, HolidayState

from fastapi import status
from httpx import AsyncClient
import pytest


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize(
    "request_string, status_code, case",
    [
        (
            "http://127.0.0.1:8000/holidays?year=2025&month=10&state__name__in=CA%2CAL",
            status.HTTP_200_OK,
            1,
        ),
        (
            "http://127.0.0.1:8000/holidays?year=2025&month=10&start_date=2025-10-10",
            status.HTTP_404_NOT_FOUND,
            2,
        ),
        (
            "http://127.0.0.1:8000/holidays?start_date=2025-10-01&end_date=2025-12-20",
            status.HTTP_200_OK,
            3,
        ),
        (
            "http://127.0.0.1:8000/holidays",
            status.HTTP_200_OK,
            4,
        ),
    ],
)
async def test_get_holidays(
    client: AsyncClient, request_string: str, status_code: int, case: int
):
    response = await client.get(request_string)

    assert response.status_code == status_code

    match case:
        case 1:
            assert response.json() == [
                {
                    "name": "Testing Local Day",
                    "date": "2025-10-10",
                    "states": ["AL", "CA"],
                }
            ]

        case 2:
            assert response.json() == {"detail": "Wrong path parameters"}

        case 3:
            res = response.json()

            assert len(res) == 1
            assert res[0]["name"] == "Testing Local Day"

        case 4:
            res = response.json()

            assert len(res) == 2
            assert res[0]["name"] == "Testing National Day"
            assert res[1]["name"] == "Testing Local Day"


@pytest.mark.asyncio(loop_scope="module")
class TestUnauthorized:
    async def test_create_holiday(self, client: AsyncClient):
        response = await client.post(
            url="http://127.0.0.1:8000/holidays",
            json={"name": "Test Post Day", "date": "2025-06-27", "states": ["CA"]},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Unauthorized"}

    async def test_update_holiday_by_id(self, client: AsyncClient):
        response = await client.put(
            url="http://127.0.0.1:8000/holidays/1",
            json={"name": "Test Post Day", "date": "2025-06-27", "states": ["CA"]},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Unauthorized"}

    async def test_delete_holiday_by_id(self, client: AsyncClient):
        response = await client.delete(
            url="http://127.0.0.1:8000/holidays/1",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.asyncio(loop_scope="module")
class TestAuthorized:
    @pytest.mark.parametrize(
        "new_holiday, status_code, case",
        [
            (
                {"name": "Test Post Day", "date": "2025-05-01", "states": ["CA"]},
                status.HTTP_201_CREATED,
                1,
            ),
            (
                {"name": "Testing Day2", "date": "2025-12-01", "states": ["OO"]},
                status.HTTP_404_NOT_FOUND,
                2,
            ),
            (
                {"name": "Testing Local Day", "date": "2025-12-01", "states": ["NY"]},
                status.HTTP_409_CONFLICT,
                3,
            ),
        ],
    )
    async def test_create_holiday(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        get_jwt,
        new_holiday,
        status_code: int,
        case: int,
    ):
        response = await client.post(
            url="http://127.0.0.1:8000/holidays",
            headers={"Authorization": "Bearer " + get_jwt},
            json=new_holiday,
        )

        assert response.status_code == status_code

        match case:
            case 1:
                db_holiday = await db_session.scalar(
                    select(Holiday).filter_by(name="Test Post Day")
                )

                assert db_holiday is not None

                await db_session.delete(db_holiday)
                await db_session.commit()

            case 2:
                assert response.json() == {"detail": "No such state exists in database"}

            case 3:
                assert response.json() == {
                    "detail": f"Holiday with the name: {new_holiday['name']} already exists in database"
                }

    @pytest.mark.parametrize(
        "new_holiday, status_code, case",
        [
            (
                {"name": "Test Update Day", "date": "2025-05-01", "states": ["CA"]},
                status.HTTP_405_METHOD_NOT_ALLOWED,
                1,
            ),
            (
                {"name": "Test Update Day", "date": "2025-05-01", "states": ["OOO"]},
                status.HTTP_404_NOT_FOUND,
                2,
            ),
            (
                {"name": "Test Update Day", "date": "2025-12-01", "states": ["NY"]},
                status.HTTP_200_OK,
                3,
            ),
            (
                {"name": "Test Update Day", "date": "2025-12-01", "states": ["NY"]},
                status.HTTP_404_NOT_FOUND,
                4,
            ),
        ],
    )
    async def test_update_holiday_by_id(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        get_jwt,
        new_holiday,
        status_code: int,
        case: int,
    ):
        match case:
            case 1 | 2:
                id = case

            case 3:
                id = 2

            case _:
                id = 200

        response = await client.put(
            url=f"http://127.0.0.1:8000/holidays/{id}",
            headers={"Authorization": "Bearer " + get_jwt},
            json=new_holiday,
        )

        assert response.status_code == status_code

        match case:
            case 1:
                assert response.json() == {
                    "detail": f"Holiday with id {id} is not custom. You can change or delete holidays only downloaded by users"
                }

            case 2:
                assert response.json() == {"detail": "No such state exists in database"}

            case 3:
                updated_holiday = await db_session.scalar(
                    select(Holiday)
                    .filter_by(id=id)
                    .options(
                        selectinload(Holiday.states).joinedload(HolidayState.state)
                    )
                )

                assert updated_holiday is not None
                assert updated_holiday.name == new_holiday["name"]
                assert [
                    hst.state.name for hst in updated_holiday.states
                ] == new_holiday["states"]

            case 4:
                assert response.json() == {
                    "detail": f"Holiday with id {id} was not found"
                }

    @pytest.mark.parametrize(
        "status_code, case",
        [
            (status.HTTP_405_METHOD_NOT_ALLOWED, 1),
            (status.HTTP_204_NO_CONTENT, 2),
            (status.HTTP_404_NOT_FOUND, 3),
        ],
    )
    async def test_delete_holiday_by_id(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        get_jwt,
        status_code: int,
        case: int,
    ):
        match case:
            case 1 | 2:
                id = case

            case _:
                id = 200

        response = await client.delete(
            url=f"http://127.0.0.1:8000/holidays/{id}",
            headers={"Authorization": "Bearer " + get_jwt},
        )

        assert response.status_code == status_code

        match case:
            case 1:
                assert response.json() == {
                    "detail": f"Holiday with id {id} is not custom. You can change or delete holidays only downloaded by users"
                }

            case 3:
                assert response.json() == {
                    "detail": f"Holiday with id {id} was not found"
                }
