# redis_pubsub

A small Python package wrapping [redis-py](https://github.com/redis/redis-py) pub/sub into `Publisher` and `Subscriber` classes, with a shared, centralized connection config.

## Features

- `Publisher` / `Subscriber` classes sharing a common `RedisClientBase` connection setup
- Plain string, JSON, and base64-encoded image messages
- Centralized configuration via `RedisConfig`
- Subscriber runs message handling in a background thread

## Project structure

```
main.py                    # usage example
redis_pubsub/
├── __init__.py             # exports RedisConfig, Publisher, Subscriber
├── config.py               # RedisConfig dataclass (host/port/db/...)
├── client.py                # RedisClientBase - shared connection setup
├── publisher.py             # Publisher: publish / publish_json / publish_image
└── subscriber.py             # Subscriber: subscribe / subscribe_image / start / stop
requirements.txt
```

## Requirements

- Python 3.10+
- A running Redis server (e.g. via Docker)

## Quick start

1. Start a Redis server:

   ```bash
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the example:

   ```bash
   python3 main.py
   ```

   This publishes a string and a JSON message on the `notifications` channel, and publishes every file found in `image_src/` on the `notify-image` channel. A subscriber running in a background thread prints received notifications and saves received images into `image_dst/`.

## Usage

```python
from redis_pubsub import Publisher, RedisConfig, Subscriber

config = RedisConfig(host="localhost", port=6379)

subscriber = Subscriber(config)
subscriber.subscribe("notifications", lambda message: print(message["data"]))
subscriber.start()

publisher = Publisher(config)
publisher.publish("notifications", "Hello subscribers!")
publisher.publish_json("notifications", {"event": "user.signup", "id": 42})

subscriber.stop()
```

### Publishing/receiving images

```python
publisher.publish_image("notify-image", "path/to/photo.jpg")

def save_image(filename, image_bytes):
    with open(filename, "wb") as f:
        f.write(image_bytes)

subscriber.subscribe_image("notify-image", save_image)
```
