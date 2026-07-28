import glob
import os
import time

from redis_pubsub import Publisher, RedisConfig, Subscriber

# Source folder images are read from, and destination folder where images
# received over the "notify-image" channel get saved.
IMAGE_SRC_DIR = os.path.join(os.path.dirname(__file__), "image_src")
IMAGE_DST_DIR = os.path.join(os.path.dirname(__file__), "image_dst")


def handle_notification(message):
    # Raw handler for plain string / JSON messages on the "notifications" channel.
    print(f"Got: {message['data']}")


def handle_image(filename, image_bytes):
    # Called by Subscriber.subscribe_image with the decoded (filename, bytes)
    # instead of the raw message, so we just need to write the file out.
    os.makedirs(IMAGE_DST_DIR, exist_ok=True)
    dst_path = os.path.join(IMAGE_DST_DIR, filename)
    with open(dst_path, "wb") as f:
        f.write(image_bytes)
    print(f"Got image: {filename} ({len(image_bytes)} bytes) -> saved to {dst_path}")


def main():
    config = RedisConfig()

    # Register handlers before start(): notifications on one channel, images on
    # a separate channel since each uses a different message format/handler.
    subscriber = Subscriber(config)
    subscriber.subscribe("notifications", handle_notification)
    subscriber.subscribe_image("notify-image", handle_image)
    subscriber.start()  # spawns the background thread that delivers messages

    publisher = Publisher(config)
    publisher.publish("notifications", "Hello subscribers!")
    publisher.publish_json("notifications", {"event": "user.signup", "id": 55888})

    # Publish every file in image_src/ (base64-encoded) as JSON.
    for image_path in glob.glob(os.path.join(IMAGE_SRC_DIR, "*")):
        publisher.publish_image("notify-image", image_path)

    # Give the background thread time to process messages before we stop it.
    time.sleep(1)
    subscriber.stop()


if __name__ == "__main__":
    main()
