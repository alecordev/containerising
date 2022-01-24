import json
import time
import datetime

from rabbit import RabbitMQClient, Message

rabbitmq_client = RabbitMQClient(
    hostname="localhost",
    port=5672,
    username="guest",
    password="guest",
)

rabbitmq_client.setup_bindings(
    exchange="test", exchange_type="topic", queue_name="test", routing_key="test"
)


def do_work(message: Message):
    obj = json.loads(message.body)
    print(f"{datetime.datetime.utcnow()} {obj}")
    time.sleep(3)
    message.ack()


rabbitmq_client.start_consuming(prefetch_count=1,
                                queue_name='test',
                                on_message_callback=do_work)
