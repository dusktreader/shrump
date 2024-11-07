from typing import cast

from loguru import logger

from api.schemas import Event, Pin, PinDropped
from api.storage import get_pin_collection
from api.constants import EventKind
from api.exceptions import EventHandlerError
from api.logging import log_error


async def create_pin(event: PinDropped) -> None:
    # This should be more efficient instead of creating a new client, etc for each event
    pin_collection = get_pin_collection()
    pin_count = await pin_collection.count_documents(dict(_id=event.pin_id))
    if pin_count > 0:
        logger.warning(f"A pin with {event.pin_id=} already exists. Skipping creation")
        return

    new_pin = Pin(
        _id=event.pin_id,
        owner_id=event.user_id,
        moment_created=event.moment,
        moment_last_updated=event.moment,
        coords=event.coords
    )
    await pin_collection.insert_one(new_pin.model_dump(by_alias=True))
    logger.debug(f"Inserted new pin with {event.pin_id=}")


async def event_handler(event: Event) -> None:
    with EventHandlerError.handle_errors("Failed to handle event", do_except=log_error):
        match event.kind:
            case EventKind.PIN_DROPPED:
                await create_pin(cast(PinDropped, event))
            case _:
                raise EventHandlerError("No handler registered for {event=}")
