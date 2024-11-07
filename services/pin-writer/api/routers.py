import uuid

from armasec import TokenPayload
from fastapi import APIRouter, Depends
from fastapi import status
from pydantic import UUID4

from api.controllers import drop_pin
from api.permissions import Permissions
from api.security import guard
from api.schemas import Coords

command_router = APIRouter(prefix="/commands", tags=["Pin commands API"])


@command_router.post(
    "/drop-pin",
    status_code=status.HTTP_201_CREATED,
    description="Endpoint used to drop a pin",
)
async def drop_pin_post(
    coords: Coords,
    token_payload: TokenPayload = Depends(guard.lockdown(Permissions.WRITE_PINS)),
) -> UUID4:
    identity: uuid.UUID = await drop_pin(coords, token_payload.sub)
    return identity
