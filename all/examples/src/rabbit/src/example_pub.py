# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "amqpstorm>=3.1",
#     "pika>=1.4",
#     "python-dotenv>=1.2",
# ]
# ///

import json
import random

import rabbit
from rabbit import RabbitMQClient

rabbitmq_client = RabbitMQClient(
    hostname=rabbit.RABBITMQ_HOST,
    port=rabbit.RABBITMQ_PORT,
    username=rabbit.RABBITMQ_USERNAME,
    password=rabbit.RABBITMQ_PASSWORD,
)

rabbitmq_client.setup_bindings(
    exchange="test", exchange_type="topic", queue_name="test", routing_key="test"
)

for _ in range(10):
    rabbitmq_client.publish(
        queue_name="test",
        body=json.dumps({"message": "hello", "value": random.random()}),
    )
