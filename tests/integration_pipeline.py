"""Live integration checks for idempotent storage and both dead-letter queues.

Run inside the Storage container after copying the file to /tmp. The script creates
and removes one synthetic database row. It also sends one invalid message through
each application queue, verifies the matching DLQ, then removes only its own test
messages from those DLQs.
"""

import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone

import mysql.connector
import pika


sys.path.insert(0, "/app")
from database.storage import StorageConsumer  # noqa: E402


DEAD_LETTER_EXCHANGE = os.getenv("DEAD_LETTER_EXCHANGE", "dead_letter")
RAW_QUEUE = os.getenv("RAW_NEWS_QUEUE", "raw_news")
ANALYTICS_QUEUE = os.getenv("ANALYTICS_QUEUE", "enriched_news")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672")


def db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "mysql"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "crypto"),
        password=os.getenv("MYSQL_PASSWORD", "crypto"),
        database=os.getenv("MYSQL_DATABASE", "crypto"),
    )


def cleanup_database(article_id, source):
    with db_connection() as database:
        with database.cursor() as cursor:
            cursor.execute("DELETE FROM analytics_hourly WHERE source = %s", (source,))
            cursor.execute("DELETE FROM pipeline_hourly WHERE source = %s", (source,))
            cursor.execute("DELETE FROM news_articles WHERE article_id = %s", (article_id,))
        database.commit()


def check_idempotence(run_id):
    article_id = (run_id * 64)[:64]
    source = f"__integration_check_{run_id}"
    now = datetime.now(timezone.utc).isoformat()
    article = {
        "article_id": article_id,
        "source": source,
        "title": "Synthetic integration check",
        "summary": "This row must be stored exactly once.",
        "url": f"https://integration.invalid/{run_id}",
        "published_at": now,
        "collected_at": now,
        "sentiment_score": 0.0,
        "sentiment_label": "neutral",
        "topics": ["other"],
    }

    cleanup_database(article_id, source)
    try:
        storage = StorageConsumer()
        first = storage.store(article)
        second = storage.store(article)
        with db_connection() as database:
            with database.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM news_articles WHERE article_id = %s",
                    (article_id,),
                )
                article_count = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT COALESCE(SUM(article_count), 0) FROM analytics_hourly WHERE source = %s",
                    (source,),
                )
                analytics_count = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT COALESCE(SUM(article_count), 0) FROM pipeline_hourly WHERE source = %s",
                    (source,),
                )
                pipeline_count = cursor.fetchone()[0]

        assert first is True, "the first insert was not accepted"
        assert second is False, "the duplicate insert was not rejected"
        assert article_count == 1, f"expected one article, got {article_count}"
        assert analytics_count == 1, f"analytics incremented {analytics_count} times"
        assert pipeline_count == 1, f"pipeline incremented {pipeline_count} times"
        print("PASS idempotence: duplicate delivery produced one article and one aggregation")
    finally:
        cleanup_database(article_id, source)


def declare_queue(channel, queue_name):
    dlq = f"{queue_name}.dlq"
    channel.exchange_declare(
        exchange=DEAD_LETTER_EXCHANGE,
        exchange_type="direct",
        durable=True,
    )
    channel.queue_declare(queue=dlq, durable=True)
    channel.queue_bind(
        exchange=DEAD_LETTER_EXCHANGE,
        queue=dlq,
        routing_key=queue_name,
    )
    channel.queue_declare(
        queue=queue_name,
        durable=True,
        arguments={"x-dead-letter-exchange": DEAD_LETTER_EXCHANGE},
    )
    return dlq


def remove_test_message(channel, dlq, message_id):
    preserved = []
    found = False
    while True:
        method, properties, body = channel.basic_get(queue=dlq, auto_ack=False)
        if method is None:
            break
        channel.basic_ack(method.delivery_tag)
        if properties.message_id == message_id:
            found = True
        else:
            preserved.append((body, properties))

    for body, properties in preserved:
        channel.basic_publish(
            exchange="",
            routing_key=dlq,
            body=body,
            properties=properties,
        )
    return found


def check_dlq(channel, queue_name, run_id):
    dlq = declare_queue(channel, queue_name)
    message_id = f"integration-invalid-{queue_name}-{run_id}"
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=f"invalid-json-{run_id}".encode("utf-8"),
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent,
            content_type="application/json",
            message_id=message_id,
        ),
    )

    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if remove_test_message(channel, dlq, message_id):
            print(f"PASS DLQ: invalid message from {queue_name} reached {dlq}")
            return
        time.sleep(0.5)
    raise AssertionError(f"test message did not reach {dlq}")


def main():
    run_id = uuid.uuid4().hex[:12]
    check_idempotence(run_id)
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    try:
        channel = connection.channel()
        check_dlq(channel, RAW_QUEUE, run_id)
        check_dlq(channel, ANALYTICS_QUEUE, run_id)
    finally:
        connection.close()
    print("All live integration checks passed")


if __name__ == "__main__":
    main()
