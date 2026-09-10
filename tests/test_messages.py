import copy
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

# Append after the standard library: app/queue must never shadow stdlib queue.
sys.path.append(str(Path(__file__).resolve().parents[1] / "app"))

from app.common.messages import validate_article  # noqa: E402
from app.queue.database.storage import StorageConsumer  # noqa: E402


def valid_article():
    return {
        "article_id": "a" * 64,
        "source": "Example",
        "title": "Bitcoin news",
        "url": "https://example.test/article",
        "summary": "",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "topics": ["bitcoin"],
        "sentiment_label": "neutral",
        "sentiment_score": 0,
    }


class MessageTests(unittest.TestCase):
    def test_valid_enriched_article(self):
        validate_article(valid_article(), enriched=True)

    def test_rejects_malformed_payloads(self):
        for payload in (None, [], "text", 1, {}, {"title": "x"}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                validate_article(payload)

    def test_rejects_invalid_fields(self):
        for field, value in (
            ("article_id", "x"),
            ("source", "s" * 121),
            ("url", "javascript:alert(1)"),
            ("topics", ["bitcoin", "bitcoin"]),
            ("topics", [{}]),
            ("sentiment_score", float("nan")),
            ("sentiment_score", True),
            ("published_at", "2026-01-01"),
        ):
            article = copy.deepcopy(valid_article())
            article[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_article(article, enriched=True)

    @patch.object(StorageConsumer, "connect_db")
    def test_expired_replay_does_not_increment_retained_aggregates(self, connect):
        article = valid_article()
        article["published_at"] = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
        self.assertFalse(StorageConsumer().store(article))
        connect.assert_not_called()

    @patch.object(StorageConsumer, "connect_db")
    def test_invalid_message_never_reaches_database(self, connect):
        with self.assertRaises(ValueError):
            StorageConsumer().store({})
        connect.assert_not_called()


class SchemaTests(unittest.TestCase):
    def test_bootstrap_and_runtime_schema_match(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(
            (root / "script/createTableCrypto.sql").read_text(),
            (root / "app/common/schema.sql").read_text(),
        )
