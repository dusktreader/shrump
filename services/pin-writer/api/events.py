import nats
import nats.aio.client
import nats.js.client
from loguru import logger

from api.config import settings
from api.logging import log_error
from api.schemas import Event
from api.exceptions import EventServiceError


class EventService:
    nats_client: nats.aio.client.Client | None
    jetstream_context: nats.js.client.JetStreamContext | None

    def __init__(self):
        self.nats_client = None
        self.jetstream_context = None

    async def get_context(self) -> nats.js.client.JetStreamContext:
        with EventServiceError.handle_errors(
            "Failed to connect to event bus",
            do_except=log_error,
        ):
            if self.nats_client is None:
                logger.debug("Connecting to nats client")
                self.nats_client = await nats.connect(
                    [f"nats://{srv}:{settings.NATS_PORT}" for srv in settings.NATS_SERVERS]
                )
            client: nats.aio.client.Client = self.nats_client

            if self.jetstream_context is None:
                logger.debug("Getting jetstream context")
                self.jetstream_context = client.jetstream()
                # TODO: set a timeout from settings
            context: nats.js.client.JetStreamContext = self.jetstream_context

            await context.add_stream(
                name=settings.NATS_STREAM,
                subjects=[settings.NATS_SUBJECT],
                # Consider subject.*
            )

        return context

    async def disconnect(self):
        if self.client is not None:
            self.client.flush()
            self.client.close()
            self.client = None
        self.jetstream_context = None

    async def send(self, event: Event) -> None:
        logger.debug(f"Dispatching event: {event=}")
        js = await self.get_context()
        with EventServiceError.handle_errors(
            "Failed to publish to the event bus",
            do_except=log_error,
        ):
            subject = settings.NATS_SUBJECT
            ack = await js.publish(subject, event.model_dump_json().encode())
        logger.debug(f"Event bus acknowledgement: {ack.stream=}, {ack.seq=}")


event_service = EventService()
