from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class JWTSettings(BaseSettings):
    private_key_path: Path = BASE_DIR / "creds" / "rsa.pem"
    public_key_path: Path = BASE_DIR / "creds" / "rsa.pub"
    lifetime_seconds: int = 120
    algorithm: str = "RS256"
    RESET_PASSWORD_TOKEN_SECRET: str
    VERIFICATION_TOKEN_SECRET: str

    model_config = SettingsConfigDict(env_file=BASE_DIR.parent.parent / ".env")


class Settings(JWTSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()  # type: ignore
