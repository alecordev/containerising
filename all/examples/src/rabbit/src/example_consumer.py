# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "amqpstorm>=3.1",
#     "pika>=1.4",
#     "python-dotenv>=1.2",
# ]
# ///

import json
import time
import datetime

import rabbit
from rabbit import RabbitMQClient, Message

rabbitmq_client = RabbitMQClient(
    hostname=rabbit.RABBITMQ_HOST,
    port=rabbit.RABBITMQ_PORT,
    username=rabbit.RABBITMQ_USERNAME,
    password=rabbit.RABBITMQ_PASSWORD,
)

rabbitmq_client.setup_bindings(
    exchange="test", exchange_type="topic", queue_name="test", routing_key="test"
)


def do_work(message: Message):
    obj = json.loads(message.body)
    print(f"{datetime.datetime.now(datetime.timezone.utc)} {obj}")
    time.sleep(3)
    message.ack()


rabbitmq_client.start_consuming(prefetch_count=1,
                                queue_name='test',
                                on_message_callback=do_work)
