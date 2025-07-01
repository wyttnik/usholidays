from fastapi_users.authentication import (
    BearerTransport,
    JWTStrategy,
)
from core.config import settings

bearer_transport = BearerTransport(tokenUrl="auth/login")


def get_jwt_strategy():
    return JWTStrategy(
        secret=settings.private_key_path.read_text(),
        lifetime_seconds=settings.lifetime_seconds,
        algorithm=settings.algorithm,
        public_key=settings.public_key_path.read_text(),
    )
