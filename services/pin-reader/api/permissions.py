from enum import Enum


class Permissions(str, Enum):
    READ_PINS = "pins:read"
