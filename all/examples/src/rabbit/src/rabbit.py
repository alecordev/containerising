import os
import json
import time
import datetime
import uuid
from typing import Callable

from amqpstorm import Message, Connection
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT"))
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")

RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE")
RABBITMQ_EXCHANGE_TYPE = os.getenv("RABBITMQ_EXCHANGE_TYPE")
RABBITMQ_QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME")
RABBITMQ_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY")


class RPCClient:

    def __init__(
        self,
        hostname: str,
        port: int,
        username: str,
        password: str,
        heartbeat_interval: int = 60,
    ):
        self.connection = Connection(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            heartbeat=heartbeat_interval,
        )
        self.channel = self.connection.channel()
        result = self.channel.queue.declare(exclusive=True, auto_delete=True)
        self.callback_queue = result["queue"]
        self.channel.basic.consume(
            self.on_response, no_ack=True, queue=self.callback_queue
        )

    def on_response(self, message: Message):
        self.response = message.body

    def call(self, queue_name: str, message: str, exchange_name: str = ""):
        self.response = None
        message = Message.create(self.channel, body=message)
        message.reply_to = self.callback_queue
        self.correlation_id = message.correlation_id
        message.publish(exchange=exchange_name, routing_key=queue_name)

        while not self.response:
            self.channel.process_data_events()
            time.sleep(0.001)

        return self.response

    def close(self):
        self.channel.stop_consuming()
        self.channel.close()
        self.connection.close()


class RPCConsumer:

    def __init__(
        self,
        hostname: str,
        port: int,
        username: str,
        password: str,
        queue_name: str,
        callback: Callable,
        timeout: int = 300,
        heartbeat_interval: int = 60,
        auto_delete: bool = True,
    ):
        self.callback = callback
        self.connection = Connection(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            heartbeat=heartbeat_interval,
        )
        self.channel = self.connection.channel(rpc_timeout=timeout)
        self.channel.queue.declare(queue=queue_name, auto_delete=auto_delete)
        self.channel.basic.qos(prefetch_count=1)
        self.channel.basic.consume(self.on_request, queue=queue_name)
        self.channel.start_consuming()

    def on_request(self, message):
        result = self.callback(message.body)
        response = Message.create(
            message.channel, result, {"correlation_id": message.correlation_id}
        )
        response.publish(message.reply_to)
        message.ack()


class RabbitMQClient:
    def __init__(
        self,
        hostname: str,
        port: int,
        username: str,
        password: str,
        heartbeat_interval: int = 60,
    ):
        self.connection = Connection(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            heartbeat=heartbeat_interval,
        )

        self.channel = self.connection.channel()

    def setup_bindings(
        self,
        exchange: str,
        exchange_type: str,
        queue_name: str,
        routing_key: str,
        durable_exchange=True,
        durable_queue=True,
        arguments=None,
    ):
        self.channel.exchange.declare(
            exchange=exchange,
            exchange_type=exchange_type,
            auto_delete=False,
            durable=durable_exchange,
        )
        self.channel.queue.declare(
            queue=queue_name, arguments=arguments, durable=durable_queue
        )
        self.channel.queue.bind(
            queue=queue_name, exchange=exchange, routing_key=routing_key
        )

    def start_consuming(
        self, queue_name: str, on_message_callback, prefetch_count: int = 1
    ):
        self.channel.basic.qos(prefetch_count=prefetch_count)
        self.channel.basic.consume(on_message_callback, queue=queue_name, no_ack=False)
        self.channel.start_consuming()

    def publish(self, queue_name: str, body: str, properties: {} = None, priority=None):
        message = Message(channel=self.channel, body=body, properties=properties)
        message.priority = priority
        message.publish(queue_name)


class Service:
    """ Example of how to use the logic """
    def __init__(self):
        self.rabbitmq_consumer = RabbitMQClient(
            hostname=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            username=RABBITMQ_USERNAME,
            password=RABBITMQ_PASSWORD,
        )

        self.rabbitmq_consumer.setup_bindings(
            exchange=RABBITMQ_EXCHANGE,
            exchange_type=RABBITMQ_EXCHANGE_TYPE,
            queue_name=RABBITMQ_QUEUE_NAME,
            routing_key=RABBITMQ_ROUTING_KEY,
        )

        self.rabbitmq_consumer.start_consuming(
            prefetch_count=1,
            queue_name=RABBITMQ_QUEUE_NAME,
            on_message_callback=self.handle_message,
        )

    def handle_message(self, message: Message):
        obj = json.loads(message.body)
        document = {
            "id": obj["id"],
            "date": obj["object_name"],
        }
        print(f"Received:\n{json.dumps(document, indent=4)}")
        message.ack()


def send_message():
    RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")
    RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT"))
    RABBITMQ_USERNAME = os.environ.get("RABBITMQ_USERNAME")
    RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD")

    RABBITMQ_EXCHANGE = os.environ.get("RABBITMQ_EXCHANGE")
    RABBITMQ_EXCHANGE_TYPE = os.environ.get("RABBITMQ_EXCHANGE_TYPE")
    RABBITMQ_QUEUE_NAME = os.environ.get("RABBITMQ_QUEUE_NAME")
    RABBITMQ_ROUTING_KEY = os.environ.get("RABBITMQ_ROUTING_KEY")

    rabbitmq_client = RabbitMQClient(
        hostname=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        username=RABBITMQ_USERNAME,
        password=RABBITMQ_PASSWORD,
    )

    rabbitmq_client.setup_bindings(
        exchange=RABBITMQ_EXCHANGE,
        exchange_type=RABBITMQ_EXCHANGE_TYPE,
        queue_name=RABBITMQ_QUEUE_NAME,
        routing_key=RABBITMQ_ROUTING_KEY,
    )

    rabbitmq_client.publish(
        queue_name="test",
        body=json.dumps(
            {
                "date": str(datetime.datetime.utcnow()),
                "object_name": "start_job",
                "id": str(uuid.uuid4()),
            }
        ),
    )


if __name__ == "__main__":
    # Message - publisher and consumer.
    send_message()
    Service()
