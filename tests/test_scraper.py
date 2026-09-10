import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "app" / "scrap"))
from cryptoscrap import CryptoNewsScraper  # noqa: E402


class Feed(dict):
    __getattr__ = dict.__getitem__


class ScraperTests(unittest.TestCase):
    @patch.object(CryptoNewsScraper, "_fetch")
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


class FetchTests(unittest.TestCase):
    @patch("cryptoscrap._OPENER.open")
    def test_rejects_oversized_feed(self, open_url):
        open_url.return_value.__enter__.return_value.read.return_value = b"x" * (
            2 * 1024 * 1024 + 1
        )
        with self.assertRaises(ValueError):
            CryptoNewsScraper._fetch("https://example.test/rss")
        self.assertEqual(open_url.call_args.kwargs["timeout"], 15)

    @patch("cryptoscrap._OPENER.open")
    def test_rejects_local_file(self, open_url):
        with self.assertRaises(ValueError):
            CryptoNewsScraper._fetch("file:///etc/passwd")
        open_url.assert_not_called()

    @patch.object(CryptoNewsScraper, "_fetch", side_effect=TimeoutError)
    def test_timeout_skips_source(self, fetch):
        self.assertEqual(CryptoNewsScraper(["https://example.test/rss"]).collect(), [])


class RedirectTests(unittest.TestCase):
    def test_rejects_ftp_redirect(self):
        from cryptoscrap import HTTPOnlyRedirects

        with self.assertRaises(ValueError):
            HTTPOnlyRedirects().redirect_request(None, None, 302, "", {}, "ftp://example.test/file")
