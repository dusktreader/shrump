import dataclasses
import inspect
import logging
import sys
import traceback

from loguru import logger
from buzz import DoExceptParams

from api.config import settings


class InterceptHandler(logging.Handler):
    """
    Specialized handler to intercept log lines sent to standard logging by 3rd party tools.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        Handle emission of the log record.
        """
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


@dataclasses.dataclass
class RouteFilterParams:
    route: str
    verb: str = "GET"


class UvicornRouteFilter(logging.Filter):
    def __init__(self, rfp: RouteFilterParams):
        self.rfp = rfp

    def filter(self, record):
        return f"{self.rfp.verb} {self.rfp.route}" not in record.getMessage()



def init_logging(suppress_routes: list[RouteFilterParams] | None = None):
    if suppress_routes is None:
        suppress_routes = []

    uvicorn_logger = logging.getLogger("uvicorn.access")
    for rfp in suppress_routes:
        uvicorn_logger.addFilter(UvicornRouteFilter(rfp))

    logger.remove()
    logger.add(sys.stderr, level=settings.LOG_LEVEL)
    logger.info(f"Logging configured 📝 Level: {settings.LOG_LEVEL}")


def log_error(params: DoExceptParams):
    logger.error(
        "\n".join(
            [
                params.final_message,
                "--------",
                "Traceback:",
                "".join(traceback.format_tb(params.trace)),
            ]
        )
    )
