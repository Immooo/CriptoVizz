import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import common
import mysql.connector
import pika
from common.broker import declare_queue_with_dlq, parameters
from common.config import positive_int
from common.messages import MAX_MESSAGE_BYTES, validate_article

SCHEMA = (Path(common.__file__).with_name("schema.sql")).read_text(encoding="utf-8")
DEAD_LETTER_EXCHANGE = os.getenv("DEAD_LETTER_EXCHANGE", "dead_letter")


def utc_naive(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(tzinfo=None)


class StorageConsumer:
    def __init__(self):
        self.queue = os.getenv("ANALYTICS_QUEUE", "enriched_news")
        self.prefetch_count = positive_int("STORAGE_PREFETCH_COUNT", 50)

    @staticmethod
    def connect_db():
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "mysql"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "crypto"),
            password=os.environ["MYSQL_PASSWORD"],
            connection_timeout=10,
            database=os.getenv("MYSQL_DATABASE", "crypto"),
        )

    def ensure_schema(self):
        while True:
            try:
                with self.connect_db() as database:
                    with database.cursor() as cursor:
                        for statement in SCHEMA.split(";"):
                            if statement.strip():
                                cursor.execute(statement)
                    database.commit()
                return
            except mysql.connector.Error as exc:
                print(f"MySQL unavailable: {exc}; retrying in 5 seconds")
                time.sleep(5)

    def store(self, article):
        validate_article(article, enriched=True)
        published_at = utc_naive(article["published_at"])
        retention_days = positive_int("RETENTION_DAYS", 30)
        if retention_days <= 0:
            raise ValueError("RETENTION_DAYS must be positive")
        if published_at < datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
            days=retention_days
        ):
            return False
        collected_at = utc_naive(article["collected_at"])
        analytics_bucket = published_at.replace(minute=0, second=0, microsecond=0)
        pipeline_bucket = collected_at.replace(minute=0, second=0, microsecond=0)
        processing_time = datetime.now(timezone.utc).replace(tzinfo=None)
        latency_ms = max(0, int((processing_time - collected_at).total_seconds() * 1000))
        topics = article.get("topics") or ["other"]

        with self.connect_db() as database:
            with database.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO news_articles
                    (article_id, source, title, summary, url, published_at,
                     collected_at, sentiment_score, sentiment_label, topics)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE article_id = article_id
                    """,
                    (
                        article["article_id"],
                        article["source"],
                        article["title"],
                        article.get("summary", ""),
                        article["url"],
                        published_at,
                        collected_at,
                        article["sentiment_score"],
                        article["sentiment_label"],
                        json.dumps(topics),
                    ),
                )
                if cursor.rowcount == 0:
                    return False

                cursor.execute(
                    """
                    INSERT INTO pipeline_hourly
                    (bucket_start, source, article_count, latency_sum_ms, latency_max_ms)
                    VALUES (%s, %s, 1, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        article_count = article_count + 1,
                        latency_sum_ms = latency_sum_ms + VALUES(latency_sum_ms),
                        latency_max_ms = GREATEST(latency_max_ms, VALUES(latency_max_ms))
                    """,
                    (pipeline_bucket, article["source"], latency_ms, latency_ms),
                )

                for topic in topics:
                    label = article["sentiment_label"]
                    cursor.execute(
                        """
                        INSERT INTO analytics_hourly
                        (bucket_start, source, topic, article_count, positive_count,
                         neutral_count, negative_count, sentiment_sum)
                        VALUES (%s, %s, %s, 1, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            article_count = article_count + 1,
                            positive_count = positive_count + VALUES(positive_count),
                            neutral_count = neutral_count + VALUES(neutral_count),
                            negative_count = negative_count + VALUES(negative_count),
                            sentiment_sum = sentiment_sum + VALUES(sentiment_sum)
                        """,
                        (
                            analytics_bucket,
                            article["source"],
                            topic,
                            int(label == "positive"),
                            int(label == "neutral"),
                            int(label == "negative"),
                            article["sentiment_score"],
                        ),
                    )
            database.commit()
        return True

    def run(self):
        self.ensure_schema()
        while True:
            connection = None
            try:
                connection = pika.BlockingConnection(parameters())
                channel = connection.channel()
                declare_queue_with_dlq(channel, self.queue)
                channel.basic_qos(prefetch_count=self.prefetch_count)

                def callback(ch, method, properties, body):
                    try:
                        if len(body) > MAX_MESSAGE_BYTES:
                            raise ValueError("message too large")
                        self.store(json.loads(body))
                        ch.basic_ack(method.delivery_tag)
                    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                        print(f"Invalid analytics message discarded: {exc}")
                        ch.basic_reject(method.delivery_tag, requeue=False)
                    except (mysql.connector.DataError, mysql.connector.IntegrityError) as exc:
                        print(f"Invalid database payload: {exc}")
                        ch.basic_reject(method.delivery_tag, requeue=False)
                    except mysql.connector.Error as exc:
                        print(f"Storage failed, message requeued: {exc}")
                        ch.basic_nack(method.delivery_tag, requeue=True)
                        connection.sleep(5)

                channel.basic_consume(self.queue, callback, auto_ack=False)
                print(f"Storage consumer listening on {self.queue}")
                channel.start_consuming()
            except pika.exceptions.AMQPError as exc:
                print(f"RabbitMQ unavailable: {exc}; retrying in 5 seconds")
                time.sleep(5)
            finally:
                if connection is not None and connection.is_open:
                    connection.close()
