from fastapi import APIRouter

from auth.fastapi_users import fastapi_users, auth_backend
from auth.schemas import UserCreate, UserRead

router = APIRouter(tags=["Auth"], prefix="/auth")

# /login
# /logout
router.include_router(router=fastapi_users.get_auth_router(auth_backend))

# /register
router.include_router(router=fastapi_users.get_register_router(UserRead, UserCreate))
