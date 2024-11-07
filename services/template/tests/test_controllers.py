import pytest
from sqlalchemy import select

from api.constants import EventKind
from api.controllers import drop_pin
from api.models import Identity, Event
from api.schemas import Coords


@pytest.mark.asyncio
async def test_drop_pin__success(synth_session):
    test_coords = Coords(latitude=45.710861, longitude=122.337944)
    test_owner = "the-dude"
    event = await drop_pin(synth_session, test_coords, test_owner)

    query = select(Identity).where(Identity.owner == test_owner)
    result = await synth_session.execute(query)
    created_identity = result.scalar_one_or_none()
    assert created_identity.owner == test_owner

    query = select(Event).where(Event.identity_id == created_identity.id)
    result = await synth_session.execute(query)
    created_event = result.scalar_one_or_none()
    assert created_event.kind == EventKind.CREATED
    assert created_event.data == dict(
        created_by=test_owner,
        coords=test_coords.dict(),
    )
