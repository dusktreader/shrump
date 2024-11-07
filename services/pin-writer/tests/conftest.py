import contextlib

import pytest
from httpx import AsyncClient
from loguru import logger

from api.config import settings
from api.main import app


@pytest.fixture
def caplog(caplog):
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)


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
        token = build_rs256_token(claim_overrides=claim_overrides, format_keycloak=True)
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
