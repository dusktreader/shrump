import typing
from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from yarl import URL

from api.config import settings
from api.constants import LogLevel


def build_db_url(
    force_test: bool = False,
    asynchronous: bool = True,
) -> str:
    prefix = "TEST_" if force_test else ""
    db_user = getattr(settings, f"{prefix}DATABASE_USER")
    db_password = getattr(settings, f"{prefix}DATABASE_PSWD")
    db_host = getattr(settings, f"{prefix}DATABASE_HOST")
    db_port = getattr(settings, f"{prefix}DATABASE_PORT")
    db_name = getattr(settings, f"{prefix}DATABASE_NAME")
    db_path = "/{}".format(db_name)
    db_scheme = "postgresql+asyncpg" if asynchronous else "postgresql"

    return str(
        URL.build(
            scheme=db_scheme,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            path=db_path,
        )
    )


class EngineFactory:
    """
    Todo:
        Maybe consider publishing this to pypi because it's lame to copy this code everywhere
    """
    engine: AsyncEngine | None

    def __init__(self):
        self.engine = None

    async def cleanup(self):
        if settings.DEPLOY_ENV.lower() == "test":
            return
        if self.engine is not None:
            await self.engine.dispose()

    def get_engine(self) -> AsyncEngine:
        db_url = build_db_url(
            force_test=settings.DEPLOY_ENV.lower() == "test",
        )
        kwargs = dict(
            logging_name="sqlalchemy.engine",
            echo=settings.LOG_LEVEL == LogLevel.TRACE,
        )
        if settings.DEPLOY_ENV.lower() == "test":
            kwargs["poolclass"] = NullPool

        self.engine = create_async_engine(db_url, **kwargs)
        return self.engine

    @asynccontextmanager
    async def auto_session(self, commit: bool = True) -> typing.AsyncIterator[AsyncSession]:
        if settings.DEPLOY_ENV.lower() == "test":
            raise RuntimeError("The auto_session context manager may not be used in unit tests.")

        engine = self.get_engine()
        session = AsyncSession(engine)
        await session.begin()

        try:
            yield session
        except Exception as err:
            logger.warning(f"Rolling back session due to error: {err}")
            await session.rollback()
            raise err
        else:
            if commit is True:
                logger.debug("Committing session")
                await session.commit()
            else:
                logger.debug("Rolling back read-only session")
                await session.rollback()
        finally:
            logger.debug("Closing session")
            await session.close()


engine_factory = EngineFactory()
