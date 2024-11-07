from typing import Literal, Annotated, Optional

import pendulum
from pydantic import ConfigDict, BaseModel, RootModel, Field, UUID4
from pydantic.functional_validators import BeforeValidator
from pydantic_extra_types.coordinate import Latitude, Longitude
from pydantic_extra_types.pendulum_dt import DateTime

from api.constants import DEFAULT_PAGE_SIZE, EventKind


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


class PinMoved(Event):
    new_coords: Coords
    kind: Literal[EventKind.PIN_MOVED] = EventKind.PIN_MOVED


class EventDiscriminator(BaseModel):
    event: PinDropped | PinMoved = Field(..., discriminator="kind")


PyObjectId = Annotated[str, BeforeValidator(str)]

class Pin(BaseModel):
    id: UUID4 = Field(alias="_id", default=None)
    owner_id: str
    coords: Coords
    moment_created: DateTime
    moment_last_updated: DateTime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


PinLot = RootModel[list[Pin]]


class PinQueryParams(BaseModel):
    owner_id: Optional[str] = None
    created_after: Optional[DateTime] = None
    created_before: Optional[DateTime] = None
    updated_after: Optional[DateTime] = None
    updated_before: Optional[DateTime] = None


class PaginationParams(BaseModel):
    page_size: int = DEFAULT_PAGE_SIZE
    page_number: int = 0


class FlatParams(PinQueryParams, PaginationParams):
    pass


class Page(BaseModel):
    pins: PinLot
    page_size: int
    page_number: int
