import asyncio
import json
from threading import Thread
from typing import Callable, Awaitable

import nats
import nats.aio.client
import nats.errors
import nats.js.client
from loguru import logger

from api.config import settings
from api.logging import log_error
from api.schemas import Event, EventDiscriminator
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

    async def _process_batch(
        self,
        consumer: nats.js.client.JetStreamContext.PullSubscription,
        event_callback: Callable[[Event], Awaitable[None]],
    ) -> None:
        try:
            logger.debug("Attempting to fetch a batch of messages")
            # env var for batch size and timeout?
            batch = await consumer.fetch(10, timeout=1)
            logger.debug(f"Got a batch of {len(batch)} messages")
            for message in batch:
                # before or after the callback?
                logger.debug(f"Processing message {message.header}")
                await message.ack()
                data = json.loads(message.data.decode())
                logger.debug(f"Extracted data {data=}")
                discriminator = EventDiscriminator(event=data)
                logger.debug(f"Deserialized to {discriminator.event=}")
                await event_callback(discriminator.event)
        except nats.errors.TimeoutError:
            logger.debug(f"Timeout...sleeping for {5} seconds")
            # env var for interval?
            await asyncio.sleep(5)

    async def listen(self, durable_name: str, event_callback: Callable[[Event], Awaitable[None]]) -> None:
        context: nats.js.client.JetStreamContext = await self.get_context()
        consumer = await context.pull_subscribe(
            settings.NATS_SUBJECT,
            durable=durable_name,
            stream=settings.NATS_STREAM
        )
        while True:
            await self._process_batch(consumer, event_callback)


def _spin(*args):
    svc = EventService()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(svc.listen(*args))


def init_listen_thread(durable_name: str, event_callback: Callable[[Event], Awaitable[None]]) -> None:

    # Need to figure out how we should handle exceptions raised in the daemon thread
    with EventServiceError.handle_errors(
        "There was an issue starting the listening thread",
        do_except=log_error,
    ):
        listen_thread = Thread(target=_spin, args=(durable_name, event_callback), daemon=True)
        listen_thread.start()
