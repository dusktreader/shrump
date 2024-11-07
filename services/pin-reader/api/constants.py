from enum import Enum, auto

from auto_name_enum import AutoNameEnum, auto as ane_auto

DEFAULT_PAGE_SIZE: int = 25


class Sentinel(Enum):
    MISSING = auto()
    NOT_GIVEN = auto()


class DeployEnv(AutoNameEnum):
    LOCAL = ane_auto()
    TEST = ane_auto()
    DEV = ane_auto()
    QA = ane_auto()
    STAGING = ane_auto()
    PRODUCTION = ane_auto()


class LogLevel(AutoNameEnum):
    TRACE = ane_auto()
    DEBUG = ane_auto()
    INFO = ane_auto()
    WARNING = ane_auto()
    ERROR = ane_auto()
    CRITICAL = ane_auto()


class EventKind(AutoNameEnum):
    TEST_EVENT = ane_auto()
    PIN_DROPPED = ane_auto()
    PIN_MOVED = ane_auto()
