import uuid

import pendulum

from api.controllers import fetch_one_pin
from api.schemas import Pin, Coords


async def test_fetch_one_pin(mocker):
    pin_id = uuid.uuid4()
    mock_getter = mocker.patch("api.controllers.get_pin_collection")
    mock_getter.return_value.find_one = mocker.AsyncMock(return_value=dict(
        _id=pin_id,
        owner_id="The Dude",
        coords=dict(
            latitude=13,
            longitude=21,
        ),
        moment_created=pendulum.parse("2024-11-02 10:05:00"),
        moment_last_updated=pendulum.parse("2024-11-02 10:10:00"),
    ))
    pin = await fetch_one_pin(pin_id)
    assert pin == Pin(
        _id=pin_id,
        owner_id="The Dude",
        coords=Coords(
            latitude=13,
            longitude=21,
        ),
        moment_created="2024-11-02 10:05:00",
        moment_last_updated="2024-11-02 10:10:00",
    )
