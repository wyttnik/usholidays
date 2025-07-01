from sqlalchemy.orm import DeclarativeBase
from enum import Enum


class HolidayTypeEnum(str, Enum):
    national = "national"
    local = "local"


class Base(DeclarativeBase):
    pass
