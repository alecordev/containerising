# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "confluent-kafka>=2.6",
# ]
# ///

"""Tiny Kafka producer/consumer using confluent-kafka.

    python producer_consumer.py produce 10
    python producer_consumer.py consume

Env: KAFKA_BOOTSTRAP (default localhost:9092), KAFKA_TOPIC (default demo).
The topic is created on demand with the admin client.
"""

from __future__ import annotations

import os
import sys

from confluent_kafka import Consumer, KafkaException, Producer
from confluent_kafka.admin import AdminClient, NewTopic

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "demo")


def ensure_topic() -> None:
    admin = AdminClient({"bootstrap.servers": BOOTSTRAP})
    if TOPIC in admin.list_topics(timeout=10).topics:
        return
    for future in admin.create_topics([NewTopic(TOPIC, num_partitions=3, replication_factor=1)]).values():
        try:
            future.result()
        except KafkaException as exc:  # e.g. topic already exists (race)
            print(f"create_topics: {exc}")


def produce(count: int) -> None:
    ensure_topic()
    producer = Producer({"bootstrap.servers": BOOTSTRAP})

    def delivered(err, msg) -> None:
        print(f"failed: {err}" if err else f"delivered to {msg.topic()}[{msg.partition()}]@{msg.offset()}")

    for i in range(count):
        producer.produce(TOPIC, key=str(i), value=f"message {i}", callback=delivered)
        producer.poll(0)
    producer.flush()


def consume() -> None:
    consumer = Consumer(
        {
            "bootstrap.servers": BOOTSTRAP,
            "group.id": "demo-group",
            "auto.offset.reset": "earliest",
        }
    )
    consumer.subscribe([TOPIC])
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            print(f"{msg.topic()}[{msg.partition()}]@{msg.offset()} {msg.key()}: {msg.value().decode()}")
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "produce"
    if mode == "produce":
        produce(int(sys.argv[2]) if len(sys.argv) > 2 else 10)
    elif mode == "consume":
        consume()
    else:
        sys.exit(__doc__)
