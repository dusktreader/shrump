from enum import Enum


class Permissions(str, Enum):
    WRITE_PINS = "write:pins"
