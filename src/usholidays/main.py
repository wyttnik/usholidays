from fastapi import FastAPI

import uvicorn
from contextlib import asynccontextmanager
from countryholidays.views import router as holidays_router
from auth.views import router as auth_router
from core.dependencies import dispose_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await dispose_engine()


app = FastAPI(lifespan=lifespan)
app.include_router(holidays_router)
app.include_router(auth_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
