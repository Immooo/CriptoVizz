import json
import os
import time

import pika

from analytics import analyze_article


RAW_QUEUE = os.getenv("RAW_NEWS_QUEUE", "raw_news")
ANALYTICS_QUEUE = os.getenv("ANALYTICS_QUEUE", "enriched_news")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672")
PREFETCH_COUNT = int(os.getenv("ANALYTICS_PREFETCH_COUNT", "50"))
DEAD_LETTER_EXCHANGE = os.getenv("DEAD_LETTER_EXCHANGE", "dead_letter")


def declare_queue_with_dlq(channel, queue_name):
    """Declare a durable work queue and its durable dead-letter queue."""
    dead_letter_queue = f"{queue_name}.dlq"
    channel.exchange_declare(
        exchange=DEAD_LETTER_EXCHANGE,
        exchange_type="direct",
        durable=True,
    )
    channel.queue_declare(queue=dead_letter_queue, durable=True)
    channel.queue_bind(
        exchange=DEAD_LETTER_EXCHANGE,
        queue=dead_letter_queue,
        routing_key=queue_name,
    )
    channel.queue_declare(
        queue=queue_name,
        durable=True,
        arguments={"x-dead-letter-exchange": DEAD_LETTER_EXCHANGE},
    )


def run():
    while True:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            declare_queue_with_dlq(channel, RAW_QUEUE)
            declare_queue_with_dlq(channel, ANALYTICS_QUEUE)
            channel.confirm_delivery()
            channel.basic_qos(prefetch_count=PREFETCH_COUNT)

            def callback(ch, method, properties, body):
                try:
                    enriched = analyze_article(json.loads(body))
                    ch.basic_publish(
                        exchange="",
                        routing_key=ANALYTICS_QUEUE,
                        body=json.dumps(enriched).encode("utf-8"),
                        properties=pika.BasicProperties(
                            delivery_mode=pika.DeliveryMode.Persistent,
                            content_type="application/json",
                            message_id=enriched["article_id"],
                        ),
                    )
                    ch.basic_ack(method.delivery_tag)
                except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                    print(f"Invalid raw article discarded: {exc}")
                    ch.basic_reject(method.delivery_tag, requeue=False)
                except Exception as exc:
                    print(f"Analytics failed, message requeued: {exc}")
                    ch.basic_nack(method.delivery_tag, requeue=True)

            channel.basic_consume(RAW_QUEUE, callback, auto_ack=False)
            print(f"Analytics worker: {RAW_QUEUE} -> {ANALYTICS_QUEUE}")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError as exc:
            print(f"RabbitMQ unavailable: {exc}; retrying in 5 seconds")
            time.sleep(5)


if __name__ == "__main__":
    run()
