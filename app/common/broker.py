"""Shared RabbitMQ connection settings and durable queue topology."""

import os

import pika


def parameters():
    url = os.getenv("RABBITMQ_URL")
    if url:
        result = pika.URLParameters(url)
    else:
        result = pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
            credentials=pika.PlainCredentials(
                os.environ["RABBITMQ_USER"], os.environ["RABBITMQ_PASSWORD"]
            ),
        )
    result.socket_timeout = 10
    result.blocked_connection_timeout = 30
    result.heartbeat = 120
    return result


def declare_queue_with_dlq(channel, queue_name):
    exchange = os.getenv("DEAD_LETTER_EXCHANGE", "dead_letter")
    dlq = f"{queue_name}.dlq"
    channel.exchange_declare(exchange=exchange, exchange_type="direct", durable=True)
    channel.queue_declare(queue=dlq, durable=True)
    channel.queue_bind(exchange=exchange, queue=dlq, routing_key=queue_name)
    channel.queue_declare(
        queue=queue_name, durable=True, arguments={"x-dead-letter-exchange": exchange}
    )
