from pydantic_settings import BaseSettings, SettingsConfigDict

from api.constants import DeployEnv, LogLevel


class Settings(BaseSettings):
    DEPLOY_ENV: DeployEnv = DeployEnv.LOCAL

    LOG_LEVEL: LogLevel = LogLevel.DEBUG

    NATS_SERVERS: list[str] = ["nats1", "nats2", "nats3"]
    NATS_PORT: int = 4222
    NATS_STREAM: str = "shrump"
    NATS_SUBJECT: str = "events.pins"

    ARMASEC_DOMAIN: str = "keycloak.local:8080/realms/master"
    ARMASEC_AUDIENCE: str = "https://shrump.dusktreader.dev"
    ARMASEC_USE_HTTPS: bool = True
    ARMASEC_DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
