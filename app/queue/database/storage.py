import json
import os
import time
from datetime import datetime, timezone

import mysql.connector
import pika


SCHEMA = """
CREATE TABLE IF NOT EXISTS news_articles (
    article_id CHAR(64) PRIMARY KEY,
    source VARCHAR(120) NOT NULL,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    url VARCHAR(1000) NOT NULL,
    published_at DATETIME NOT NULL,
    collected_at DATETIME NOT NULL,
    sentiment_score DECIMAL(6,4) NOT NULL,
    sentiment_label ENUM('positive', 'neutral', 'negative') NOT NULL,
    topics JSON NOT NULL,
    INDEX idx_news_published (published_at),
    INDEX idx_news_source (source)
);
CREATE TABLE IF NOT EXISTS analytics_hourly (
    bucket_start DATETIME NOT NULL,
    source VARCHAR(120) NOT NULL,
    topic VARCHAR(80) NOT NULL,
    article_count INT NOT NULL DEFAULT 0,
    positive_count INT NOT NULL DEFAULT 0,
    neutral_count INT NOT NULL DEFAULT 0,
    negative_count INT NOT NULL DEFAULT 0,
    sentiment_sum DECIMAL(12,4) NOT NULL DEFAULT 0,
    PRIMARY KEY (bucket_start, source, topic),
    INDEX idx_analytics_bucket (bucket_start)
);
CREATE TABLE IF NOT EXISTS pipeline_hourly (
    bucket_start DATETIME NOT NULL,
    source VARCHAR(120) NOT NULL,
    article_count INT NOT NULL DEFAULT 0,
    latency_sum_ms BIGINT NOT NULL DEFAULT 0,
    latency_max_ms BIGINT NOT NULL DEFAULT 0,
    PRIMARY KEY (bucket_start, source),
    INDEX idx_pipeline_bucket (bucket_start)
);
"""
DEAD_LETTER_EXCHANGE = os.getenv("DEAD_LETTER_EXCHANGE", "dead_letter")


def declare_queue_with_dlq(channel, queue_name):
    """Declare a durable work queue and route rejected messages to a DLQ."""
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


def utc_naive(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(tzinfo=None)


class StorageConsumer:
    def __init__(self):
        self.queue = os.getenv("ANALYTICS_QUEUE", "enriched_news_v3")
        self.rabbitmq_url = os.getenv(
            "RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672"
        )
        self.prefetch_count = int(os.getenv("STORAGE_PREFETCH_COUNT", "50"))

    @staticmethod
    def connect_db():
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "mysql"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "crypto"),
            password=os.getenv("MYSQL_PASSWORD", "crypto"),
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
        published_at = utc_naive(article["published_at"])
        collected_at = utc_naive(article["collected_at"])
        bucket = published_at.replace(minute=0, second=0, microsecond=0)
        processing_time = datetime.now(timezone.utc).replace(tzinfo=None)
        latency_ms = max(0, int((processing_time - collected_at).total_seconds() * 1000))
        topics = article.get("topics") or ["other"]

        with self.connect_db() as database:
            with database.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT IGNORE INTO news_articles
                    (article_id, source, title, summary, url, published_at,
                     collected_at, sentiment_score, sentiment_label, topics)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        article["article_id"], article["source"], article["title"],
                        article.get("summary", ""), article["url"], published_at,
                        collected_at, article["sentiment_score"],
                        article["sentiment_label"], json.dumps(topics),
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
                    (bucket, article["source"], latency_ms, latency_ms),
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
                            bucket, article["source"], topic,
                            int(label == "positive"), int(label == "neutral"),
                            int(label == "negative"), article["sentiment_score"],
                        ),
                    )
            database.commit()
        return True

    def run(self):
        self.ensure_schema()
        while True:
            try:
                connection = pika.BlockingConnection(
                    pika.URLParameters(self.rabbitmq_url)
                )
                channel = connection.channel()
                declare_queue_with_dlq(channel, self.queue)
                channel.basic_qos(prefetch_count=self.prefetch_count)

                def callback(ch, method, properties, body):
                    try:
                        self.store(json.loads(body))
                        ch.basic_ack(method.delivery_tag)
                    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                        print(f"Invalid analytics message discarded: {exc}")
                        ch.basic_reject(method.delivery_tag, requeue=False)
                    except Exception as exc:
                        print(f"Storage failed, message requeued: {exc}")
                        ch.basic_nack(method.delivery_tag, requeue=True)

                channel.basic_consume(self.queue, callback, auto_ack=False)
                print(f"Storage consumer listening on {self.queue}")
                channel.start_consuming()
            except pika.exceptions.AMQPConnectionError as exc:
                print(f"RabbitMQ unavailable: {exc}; retrying in 5 seconds")
                time.sleep(5)
