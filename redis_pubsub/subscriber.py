import base64
import json
import logging

from .client import RedisClientBase
from .config import RedisConfig

logger = logging.getLogger(__name__)


class Subscriber(RedisClientBase):
    def __init__(self, config: RedisConfig | None = None):
        super().__init__(config)
        self.pubsub = self.connection.pubsub()
        self._thread = None

    def subscribe(self, channel: str, handler):
        self.pubsub.subscribe(**{channel: handler})

    def subscribe_image(self, channel: str, handler):
        """Wraps handler so it receives (filename, image_bytes) instead of the raw message."""

        def wrapped(message):
            payload = json.loads(message["data"])
            image_bytes = base64.b64decode(payload["data"])
            handler(payload["filename"], image_bytes)

        self.subscribe(channel, wrapped)

    def start(self, sleep_time: float = 0.01):
        """Runs callbacks in a background thread."""
        self._thread = self.pubsub.run_in_thread(
            sleep_time=sleep_time, exception_handler=self._handle_exception
        )
        return self._thread

    def _handle_exception(self, exception, pubsub, thread):
        # Swallowing keeps the worker thread's loop alive so redis-py can
        # reconnect and resubscribe on the next get_message() call, instead
        # of the thread dying silently on things like a server-side
        # client-output-buffer-limit disconnect.
        logger.warning("Subscriber error: %r", exception)

    def stop(self):
        if self._thread is not None:
            self._thread.stop()
            self._thread.join()
            self._thread = None
