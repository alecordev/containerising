import json
import random

from rabbit import RabbitMQClient

rabbitmq_client = RabbitMQClient(
    hostname="localhost",
    port=5672,
    username="guest",
    password="guest",
)

rabbitmq_client.setup_bindings(
    exchange="test", exchange_type="topic", queue_name="test", routing_key="test"
)

for _ in range(10):
    rabbitmq_client.publish(
        queue_name="test",
        body=json.dumps({"message": "hello", "value": random.random()}),
    )
