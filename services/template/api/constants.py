from auto_name_enum import AutoNameEnum, auto


class DeployEnv(AutoNameEnum):
    LOCAL = auto()
    TEST = auto()
    DEV = auto()
    QA = auto()
    STAGING = auto()
    PRODUCTION = auto()


class LogLevel(AutoNameEnum):
    TRACE = auto()
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class EventKind(AutoNameEnum):
    CREATED = auto()
