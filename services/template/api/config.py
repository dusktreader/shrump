from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.constants import DeployEnv, LogLevel


class Settings(BaseSettings):
    DEPLOY_ENV: DeployEnv = DeployEnv.LOCAL

    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    SQL_LOG_LEVEL: LogLevel = LogLevel.WARNING

    DATABASE_HOST: str = "localhost"
    DATABASE_USER: str = "local-user"
    DATABASE_PSWD: str = "local-pswd"
    DATABASE_NAME: str = "local-db"
    DATABASE_PORT: int = 5432

    # Test database settings
    TEST_DATABASE_HOST: str = "localhost"
    TEST_DATABASE_USER: str = "test-user"
    TEST_DATABASE_PSWD: str = "test-pswd"
    TEST_DATABASE_NAME: str = "test-db"
    TEST_DATABASE_PORT: int = 5433

    ARMASEC_DOMAIN: str = "keycloak.local:8080/realms/master"
    ARMASEC_USE_HTTPS: bool = Field(True)
    ARMASEC_DEBUG: bool = Field(False)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
