import json
import os
import time

import pika
from analytics import analyze_article
from common.broker import declare_queue_with_dlq, parameters
from common.config import positive_int
from common.messages import MAX_MESSAGE_BYTES, validate_article

RAW_QUEUE = os.getenv("RAW_NEWS_QUEUE", "raw_news")
ANALYTICS_QUEUE = os.getenv("ANALYTICS_QUEUE", "enriched_news")
PREFETCH_COUNT = positive_int("ANALYTICS_PREFETCH_COUNT", 50)
DEAD_LETTER_EXCHANGE = os.getenv("DEAD_LETTER_EXCHANGE", "dead_letter")


def run():
    while True:
        connection = None
        try:
            connection = pika.BlockingConnection(parameters())
            channel = connection.channel()
            declare_queue_with_dlq(channel, RAW_QUEUE)
            declare_queue_with_dlq(channel, ANALYTICS_QUEUE)
            channel.confirm_delivery()
            channel.basic_qos(prefetch_count=PREFETCH_COUNT)

            def callback(ch, method, properties, body):
                try:
                    if len(body) > MAX_MESSAGE_BYTES:
                        raise ValueError("message too large")
                    enriched = analyze_article(validate_article(json.loads(body)))
                    ch.basic_publish(
                        mandatory=True,
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

            channel.basic_consume(RAW_QUEUE, callback, auto_ack=False)
            print(f"Analytics worker: {RAW_QUEUE} -> {ANALYTICS_QUEUE}")
            channel.start_consuming()
        except pika.exceptions.AMQPError as exc:
            print(f"RabbitMQ unavailable: {exc}; retrying in 5 seconds")
            time.sleep(5)
        finally:
            if connection is not None and connection.is_open:
                connection.close()


if __name__ == "__main__":
    run()
