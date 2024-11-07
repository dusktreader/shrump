from typing import Literal

import pendulum
from pydantic import BaseModel, Field, UUID4
from pydantic_extra_types.coordinate import Latitude, Longitude
from pydantic_extra_types.pendulum_dt import DateTime

from api.constants import EventKind


class Coords(BaseModel):
    latitude: Latitude | float
    longitude: Longitude | float


class Event(BaseModel):
    pin_id: UUID4
    user_id: str
    moment: DateTime = Field(default_factory=lambda: pendulum.now(tz="UTC"))  # type: ignore
    kind: EventKind


class PinDropped(Event):
    coords: Coords
    kind: Literal[EventKind.PIN_DROPPED] = EventKind.PIN_DROPPED
