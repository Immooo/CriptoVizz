import json
import os
import time

import pika

from cryptoscrap import CryptoNewsScraper


RAW_QUEUE = os.getenv("RAW_NEWS_QUEUE", "raw_news")
DEAD_LETTER_EXCHANGE = os.getenv("DEAD_LETTER_EXCHANGE", "dead_letter")
POLL_INTERVAL_SECONDS = int(os.getenv("SCRAPE_INTERVAL_SECONDS", "60"))


def connect():
    params = pika.URLParameters(
        os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672")
    )
    while True:
        try:
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            dead_letter_queue = f"{RAW_QUEUE}.dlq"
            channel.exchange_declare(exchange=DEAD_LETTER_EXCHANGE, exchange_type="direct", durable=True)
            channel.queue_declare(queue=dead_letter_queue, durable=True)
            channel.queue_bind(exchange=DEAD_LETTER_EXCHANGE, queue=dead_letter_queue, routing_key=RAW_QUEUE)
            channel.queue_declare(
                queue=RAW_QUEUE,
                durable=True,
                arguments={"x-dead-letter-exchange": DEAD_LETTER_EXCHANGE},
            )
            channel.confirm_delivery()
            return connection, channel
        except pika.exceptions.AMQPConnectionError as exc:
            print(f"RabbitMQ unavailable: {exc}; retrying in 5 seconds")
            time.sleep(5)


def publish(channel, article):
    channel.basic_publish(
        exchange="",
        routing_key=RAW_QUEUE,
        body=json.dumps(article).encode("utf-8"),
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent,
            content_type="application/json",
            message_id=article["article_id"],
        ),
    )


if __name__ == "__main__":
    scraper = CryptoNewsScraper()
    connection, channel = connect()

    try:
        while True:
            try:
                if connection.is_closed:
                    connection, channel = connect()
                articles = scraper.collect()
                for article in articles:
                    publish(channel, article)
                print(f"Published {len(articles)} news articles to {RAW_QUEUE}")
            except (pika.exceptions.AMQPError, OSError) as exc:
                print(f"Collection cycle failed: {exc}")
                connection, channel = connect()
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        if connection and connection.is_open:
            connection.close()
