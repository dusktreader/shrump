import uuid
from loguru import logger

from api.schemas import Coords, PinDropped
from api.events import event_service


async def drop_pin(
    coords: Coords,
    owner: str,
) -> uuid.UUID:
    # TODO: Think about using correlation ids for logging to tie all log lines the request they come from
    #       https://medium.com/@sondrelg_12432/setting-up-request-id-logging-for-your-fastapi-application-4dc190aac0ea
    #       https://medium.com/gradiant-talks/identifying-fastapi-requests-in-logs-bac3284a6aa
    logger.debug(f"Dropping new pin for {owner=} at {coords=}")
    identity = uuid.uuid4()
    event = PinDropped(
        pin_id=identity,
        user_id=owner,
        coords=coords,
    )
    await event_service.send(event)
    logger.debug(f"Pin dropped for {owner=} at {coords=} with {identity=}")
    return identity
