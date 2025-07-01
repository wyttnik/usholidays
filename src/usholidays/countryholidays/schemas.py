from pydantic import BaseModel, ConfigDict, model_serializer
from datetime import date


class StateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class HolidayStateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    state: "StateSchema"

    @model_serializer
    def serialize(self):
        return f"{self.state.name}"


class HolidayCreateSchema(BaseModel):
    name: str
    date: date
    states: list[str]


class HolidayUpdateSchema(HolidayCreateSchema):
    pass


class HolidaySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    date: date
    states: list["HolidayStateSchema"]
