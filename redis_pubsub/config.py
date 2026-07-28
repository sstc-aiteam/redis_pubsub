from dataclasses import dataclass


@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    decode_responses: bool = True
