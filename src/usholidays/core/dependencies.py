from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    # async_scoped_session,
)

# from asyncio import current_task
from core.config import settings

async_engine = create_async_engine(url=settings.db_url, echo=True)
async_session_factory = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, autoflush=False, autocommit=False
)


async def get_async_session():
    async with async_session_factory() as async_session:
        yield async_session


async def dispose_engine():
    await async_engine.dispose()


# def get_scoped_session():
#     return async_scoped_session(
#         session_factory=async_session_factory,
#         scopefunc=current_task,
#     )


# async def get_async_session():
#     Async_scoped_session = get_scoped_session()
#     yield Async_scoped_session()
#     await Async_scoped_session.remove()
