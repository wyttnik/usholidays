from fastapi_users.db import SQLAlchemyBaseUserTable

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer

from core.models import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # username: Mapped[str] = mapped_column(String, unique=True)
