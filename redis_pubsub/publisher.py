import base64
import json
import os

from .client import RedisClientBase


class Publisher(RedisClientBase):
    def publish(self, channel: str, message: str) -> int:
        return self.connection.publish(channel, message)

    def publish_json(self, channel: str, data: dict) -> int:
        return self.publish(channel, json.dumps(data))

    def publish_image(self, channel: str, image_path: str) -> int:
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        return self.publish_json(
            channel,
            {
                "filename": os.path.basename(image_path),
                "data": base64.b64encode(image_bytes).decode("ascii"),
            },
        )
