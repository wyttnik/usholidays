from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    pass
    # username: str


# if one would add custom field it should be also added to User db model
class UserCreate(schemas.BaseUserCreate):
    pass
    # username: str


class UserUpdate(schemas.BaseUserUpdate):
    pass
    # username: str
