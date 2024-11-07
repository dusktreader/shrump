from api.controllers import drop_pin
from api.schemas import Coords, PinDropped


async def test_drop_pin__success(mocker):
    test_coords = Coords(latitude=45.710861, longitude=122.337944)
    test_owner = "the-dude"
    mock_send = mocker.patch("api.controllers.event_service.send")
    identity = await drop_pin(test_coords, test_owner)
    mock_send.assert_called_once()
    event: PinDropped = mock_send.call_args[0][0]
    assert event.coords == test_coords
    assert event.pin_id == identity
