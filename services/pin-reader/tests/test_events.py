import pytest
import uuid
from typing import Literal

from nats.errors import TimeoutError
from nats.aio.msg import Msg

from api.events import EventService, init_listen_thread
from api.exceptions import EventServiceError
from api.schemas import Coords, PinDropped, PinMoved


async def test_get_context__success(mocker):
    mocked_nats = mocker.patch("api.events.nats")
    mocked_nats.connect = mocker.AsyncMock()
    mocked_nats.connect.return_value.jetstream = mocker.MagicMock()
    mocked_nats.connect.return_value.jetstream.return_value = mocker.AsyncMock()

    event_service = EventService()
    await event_service.get_context()
    mocked_nats.connect.assert_called_once_with(["nats://test-nats1:14222", "nats://test-nats2:14222"])
    mocked_nats.connect.return_value.jetstream.assert_called_once()
    mocked_nats.connect.return_value.jetstream.return_value.add_stream.assert_called_once_with(
        name="shrump",
        subjects=["events.pins"],
    )


async def test_get_context__raises_exception_if_connection_fails(mocker):
    mocked_nats = mocker.patch("api.events.nats")
    mocked_nats.connect = mocker.AsyncMock()
    mocked_nats.connect.side_effect = RuntimeError("Boom!")

    event_service = EventService()
    with pytest.raises(EventServiceError, match="Failed to connect to event bus"):
        await event_service.get_context()


async def test__process_batch__pulls_batch(mocker):
    mock_client = mocker.AsyncMock()

    pin_id = uuid.uuid4()
    dummy_events = [
        PinDropped(pin_id=pin_id, user_id="The Dude", coords=Coords(latitude=13, longitude=21)),
        PinMoved(pin_id=pin_id, user_id="Walter", new_coords=Coords(latitude=37, longitude=41)),
    ]
    messages = [
        Msg(mock_client, data=event.model_dump_json().encode(), reply="dummy_reply")
        for event in dummy_events
    ]

    mock_consumer = mocker.MagicMock()
    mock_consumer.fetch = mocker.AsyncMock()
    mock_consumer.fetch.return_value = messages

    mock_callback = mocker.AsyncMock()

    event_service = EventService()
    await event_service._process_batch(mock_consumer, mock_callback)

    # Assert that fetch() was called as expected
    mock_consumer.fetch.assert_called_once_with(10, timeout=1)

    # Assert that the messages' ack() methods were called as expected
    assert [mocker.call("dummy_reply"), mocker.call("dummy_reply")] == mock_client.publish.await_args_list

    # Assert that the callback function was called with the deserialized events
    assert [mocker.call(e) for e in dummy_events] == mock_callback.await_args_list


async def test__process_batch__sleeps_if_fetch_times_out(mocker):
    mock_consumer = mocker.MagicMock()
    mock_consumer.fetch = mocker.AsyncMock(side_effect=TimeoutError)

    mock_callback = mocker.AsyncMock()
    mock_sleep = mocker.AsyncMock()
    mocker.patch("api.events.asyncio.sleep", new=mock_sleep)

    event_service = EventService()
    await event_service._process_batch(mock_consumer, mock_callback)

    # Assert that fetch() was called as expected
    mock_consumer.fetch.assert_called_once_with(10, timeout=1)

    # Assert that sleep was called at the end
    mock_sleep.assert_called_once_with(5)


async def test_init_listen_thread__success(mocker):
    mock__spin = mocker.patch("api.events._spin")
    mock_callback = mocker.AsyncMock()
    init_listen_thread("dummy-name", mock_callback)

    mock__spin.assert_called_once_with("dummy-name", mock_callback)


async def test_init_listen_thread__raises_error_if_thread_fails_to_start(mocker):
    mock_Thread = mocker.patch("api.events.Thread")
    mock_Thread.return_value.start.side_effect = RuntimeError("Boom!")
    mock_callback = mocker.AsyncMock()

    with pytest.raises(EventServiceError, match="There was an issue starting the listening thread.*Boom!"):
        init_listen_thread("dummy-name", mock_callback)

