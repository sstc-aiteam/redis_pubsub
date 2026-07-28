import redis

from .config import RedisConfig


class RedisClientBase:
    """Shared connection setup for publisher/subscriber classes."""

    def __init__(self, config: RedisConfig | None = None):
        self.config = config or RedisConfig()
        self.connection = redis.Redis(
            host=self.config.host,
            port=self.config.port,
            db=self.config.db,
            decode_responses=self.config.decode_responses,
        )
