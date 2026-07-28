import base64
import json

from .client import RedisClientBase
from .config import RedisConfig


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
        self._thread = self.pubsub.run_in_thread(sleep_time=sleep_time)
        return self._thread

    def stop(self):
        if self._thread is not None:
            self._thread.stop()
            self._thread.join()
            self._thread = None
