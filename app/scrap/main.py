import json
import os
import time

import pika
from common.broker import declare_queue_with_dlq, parameters
from common.config import positive_int
from cryptoscrap import CryptoNewsScraper

RAW_QUEUE = os.getenv("RAW_NEWS_QUEUE", "raw_news")
DEAD_LETTER_EXCHANGE = os.getenv("DEAD_LETTER_EXCHANGE", "dead_letter")
POLL_INTERVAL_SECONDS = positive_int("SCRAPE_INTERVAL_SECONDS", 60)


def connect():
    params = parameters()
    while True:
        try:
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            declare_queue_with_dlq(channel, RAW_QUEUE)
            channel.confirm_delivery()
            return connection, channel
        except pika.exceptions.AMQPConnectionError as exc:
            print(f"RabbitMQ unavailable: {exc}; retrying in 5 seconds")
            time.sleep(5)


def publish(channel, article):
    channel.basic_publish(
        mandatory=True,
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
                if connection.is_open:
                    connection.close()
                connection, channel = connect()
            connection.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        if connection and connection.is_open:
            connection.close()
