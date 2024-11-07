from armasec import Armasec
from loguru import logger

from api.config import settings


guard = Armasec(
    domain=settings.ARMASEC_DOMAIN,
    use_https=settings.ARMASEC_USE_HTTPS,
    debug_logger=logger.debug if settings.ARMASEC_DEBUG else None,
)
