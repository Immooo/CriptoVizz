import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).parents[1] / "app" / "scrap"))
if "feedparser" not in sys.modules:
    fake_feedparser = types.ModuleType("feedparser")
    fake_feedparser.parse = lambda url: None
    sys.modules["feedparser"] = fake_feedparser

from cryptoscrap import CryptoNewsScraper  # noqa: E402


class Feed(dict):
    __getattr__ = dict.__getitem__


class ScraperTests(unittest.TestCase):
    @patch("cryptoscrap.feedparser.parse")
    def test_normalizes_feed_entry(self, parse):
        parse.return_value = Feed(
            bozo=False,
            feed={"title": "Example News"},
            entries=[
                {
                    "title": "Bitcoin update",
                    "link": "https://example.test/article",
                    "summary": "Market news",
                    "published_parsed": (2026, 1, 2, 3, 4, 5, 0, 0, 0),
                }
            ],
        )

        articles = CryptoNewsScraper(["https://example.test/rss"]).collect()

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["source"], "Example News")
        self.assertEqual(articles[0]["published_at"], "2026-01-02T03:04:05+00:00")
        self.assertEqual(len(articles[0]["article_id"]), 64)


if __name__ == "__main__":
    unittest.main()
