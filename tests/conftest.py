from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from src.usholidays.core.config import settings
from src.usholidays.core.models import Base
from src.usholidays.countryholidays.views import get_async_session
from src.usholidays.main import app
from tests.utils import populate_test_db

from httpx import ASGITransport, AsyncClient
import pytest_asyncio

settings.DB_HOST = "localhost"
settings.DB_NAME = "testing"
async_engine = create_async_engine(url=settings.db_url, echo=False)
async_session_factory = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, autoflush=False, autocommit=False
)


@pytest_asyncio.fixture(scope="function", loop_scope="module")
async def db_session():
    async with async_session_factory() as async_session:
        yield async_session


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def client():
    # async def get_async_session_local():
    #     Async_scoped_session = get_scoped_session()
    #     yield Async_scoped_session()
    #     await Async_scoped_session.remove()
    async def get_session():
        async with async_session_factory() as async_session:
            yield async_session

    app.dependency_overrides[get_async_session] = get_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides = {}


@pytest_asyncio.fixture(scope="class", loop_scope="module")
async def get_jwt(client: AsyncClient):
    await client.post(
        url="http://127.0.0.1:8000/auth/register",
        json={
            "email": "user@example.com",
            "password": "string",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
        },
    )
    data = {
        "grant_type": "password",
        "username": "user@example.com",
        "password": "string",
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }
    response = await client.post(url="http://127.0.0.1:8000/auth/login", data=data)

    return response.json()["access_token"]


@pytest_asyncio.fixture(scope="module", loop_scope="module", autouse=True)
async def setup_db():
    async with async_engine.connect() as conn:
        # await conn.execute(CreateSchema("testing"))
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()
        async with AsyncSession(
            conn, expire_on_commit=False, autoflush=False, autocommit=False
        ) as session:
            await populate_test_db(session=session)

        yield
        await conn.run_sync(Base.metadata.drop_all)
        # await conn.execute(DropSchema("testing"))
        await conn.commit()
    await async_engine.dispose()
