from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend
from auth.dependencies import get_jwt_strategy, bearer_transport
from auth.dependencies import get_user_manager
from auth.models import User


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager=get_user_manager, auth_backends=[auth_backend]
)

current_active_user = fastapi_users.current_user(active=True)
