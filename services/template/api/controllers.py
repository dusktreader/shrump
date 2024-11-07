from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from api.constants import EventKind
from api.models import Identity, Event
from api.schemas import Coords


async def drop_pin(
    session: AsyncSession,
    coords: Coords,
    owner: str,
) -> Event:
    # TODO: Think about using correlation ids for logging to tie all log lines the request they come from
    #       https://medium.com/@sondrelg_12432/setting-up-request-id-logging-for-your-fastapi-application-4dc190aac0ea
    #       https://medium.com/gradiant-talks/identifying-fastapi-requests-in-logs-bac3284a6aa
    logger.debug(f"Dropping new pin for {owner=} at {coords=}")

    logger.debug(f"Creating database objects")
    identity = Identity(owner=owner)
    session.add(identity)
    await session.flush()
    await session.refresh(identity)

    event = Event(
        kind=EventKind.CREATED,
        identity_id=identity.id,
        data=dict(
            created_by=owner,
            coords=dict(
                latitude=coords.latitude,
                longitude=coords.longitude,
            )
        )
    )
    session.add(event)
    await session.flush()
    await session.refresh(event)
    logger.debug(f"Finished creating database objects")

    logger.debug(f"Dispatching event")
    # TODO: dispatch the event here
    logger.debug(f"Finished dispatching event")

    logger.debug(f"Pin dropped for {owner=} at {coords=} with identity={identity.uuid}")
    return event
