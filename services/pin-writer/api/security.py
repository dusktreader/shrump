from armasec import Armasec, extract_keycloak_permissions
from loguru import logger

from api.config import settings


guard = Armasec(
    domain=settings.ARMASEC_DOMAIN,
    audience=settings.ARMASEC_AUDIENCE,
    use_https=settings.ARMASEC_USE_HTTPS,
    debug_logger=logger.debug if settings.ARMASEC_DEBUG else None,
    permission_extractor=extract_keycloak_permissions,
)
