import asyncio
import contextlib
from contextlib import asynccontextmanager
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import Base
from api.config import settings
from api.main import app
from api.storage import engine_factory


@pytest.fixture(autouse=True, scope="session")
async def synth_engine():
    engine = engine_factory.get_engine()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all, checkfirst=True)
    try:
        yield engine
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
        await engine_factory.cleanup()


@pytest.fixture(scope="function")
async def synth_session(synth_engine):
    """
    Get a session from the engine_factory for the current test function.

    This is necessary to make sure that the test code uses the same session as the one returned by
    the dependency injection for the router code. Otherwise, changes made in the router's session would not
    be visible in the test code. Note that changes made in this synthesized session are always rolled back
    and never committed.

    NOTE:
        Any router tests that interact with endpoints that use the database MUST use this fixture or the
        session they get will not be the same session used across different routes or by the locally bound
        services.
    """
    session = AsyncSession(synth_engine)
    await session.begin()

    @asynccontextmanager
    async def auto_session(*_, **__):
        nested_transaction = await session.begin_nested()
        try:
            yield session
            await nested_transaction.commit()
        except Exception as err:
            await nested_transaction.rollback()
            raise err

    with patch("api.storage.engine_factory.auto_session", new=auto_session):
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture(autouse=True)
def enforce_mocked_oidc_provider(mock_openid_server):
    """
    Enforce that the OIDC provider used by armasec is the mock_openid_server provided as a fixture.

    No actual calls to an OIDC provider will be made.
    """
    yield


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def inject_security_header(client, build_rs256_token):
    """
    Provide a helper method that will inject a security token into the requests for a test client.

    If no permissions are provided, the security token will still be valid but will not carry any permissions.
    Uses the `build_rs256_token()` fixture from the armasec package.
    """

    def _helper(**claim_overrides):
        token = build_rs256_token(claim_overrides=claim_overrides)
        client.headers.update({"Authorization": f"Bearer {token}"})

    return _helper


@pytest.fixture
def tweak_settings():

    @contextlib.contextmanager
    def _helper(**kwargs):
        previous_values = {}
        for key, value in kwargs.items():
            previous_values[key] = getattr(settings, key)
            setattr(settings, key, value)
        yield
        for key, value in previous_values.items():
            setattr(settings, key, value)

    return _helper
