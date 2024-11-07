from armasec import TokenPayload
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi import Response as FastAPIResponse
from fastapi import status
from loguru import logger
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from api.controllers import drop_pin
from api.models import Event
from api.permissions import Permissions
from api.security import guard
from api.schemas import Coords
from api.storage import engine_factory

command_router = APIRouter(prefix="/commands", tags=["Pin commands API"])


@command_router.post(
    "drop-pin",
    status_code=status.HTTP_201_CREATED,
    description="Endpoint used to drop a pin",
)
async def drop_pin(
    coords: Coords,
    token_payload: TokenPayload = Depends(guard.lockdown(Permissions.WRITE_PINS)),
    session: AsyncSession = Depends(engine_factory.auto_session),
) -> UUID4:
    event: Event = await drop_pin(session, coords, token_payload.sub)
    return event.identity.uuid
