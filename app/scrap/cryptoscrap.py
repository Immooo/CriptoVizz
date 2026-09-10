import hashlib
import os
from datetime import datetime, timezone
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

import feedparser


class HTTPOnlyRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlsplit(newurl).scheme not in {"http", "https"}:
            raise ValueError("RSS redirects must use HTTP(S)")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_OPENER = build_opener(HTTPOnlyRedirects())


DEFAULT_FEEDS = "https://www.coindesk.com/arc/outboundfeeds/rss/,https://cointelegraph.com/rss"


class CryptoNewsScraper:
    """Collect and normalize articles from cryptocurrency RSS feeds."""

    def __init__(self, feed_urls=None):
        configured = feed_urls or os.getenv("NEWS_FEED_URLS", DEFAULT_FEEDS).split(",")
        self.feed_urls = [url.strip() for url in configured if url.strip()]

    @staticmethod
    def _fetch(feed_url):
        if urlsplit(feed_url).scheme not in {"http", "https"}:
            raise ValueError("RSS feeds must use HTTP(S)")
        request = Request(feed_url, headers={"User-Agent": "CryptoViz/1.0"})
        with _OPENER.open(request, timeout=15) as response:
            body = response.read(2 * 1024 * 1024 + 1)
        if len(body) > 2 * 1024 * 1024:
            raise ValueError("RSS feed exceeds 2 MiB")
        return feedparser.parse(body)

    @staticmethod
    def _iso_datetime(entry, field, fallback):
        parsed = entry.get(field)
        if parsed:
            return datetime(*parsed[:6], tzinfo=timezone.utc).isoformat()
        return fallback

    @staticmethod
    def _article_id(url):
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def collect(self):
        collected_at = datetime.now(timezone.utc).isoformat()
        articles = []

        for feed_url in self.feed_urls:
            try:
                feed = self._fetch(feed_url)
            except (OSError, ValueError) as exc:
                print(f"RSS request failed: {type(exc).__name__}")
                continue
            if feed.bozo and not feed.entries:
                print(f"Unable to read RSS feed {feed_url}: {feed.bozo_exception}")
                continue

            source = feed.feed.get("title", feed_url)
            for entry in feed.entries:
                url = entry.get("link") or entry.get("id")
                title = (entry.get("title") or "").strip()
                if (
                    not isinstance(url, str)
                    or urlsplit(url).scheme not in {"http", "https"}
                    or not title
                ):
                    continue

                articles.append(
                    {
                        "article_id": self._article_id(url),
                        "source": source[:120],
                        "title": title[:500],
                        "summary": (entry.get("summary") or "")[:5000],
                        "url": url[:1000],
                        "published_at": self._iso_datetime(entry, "published_parsed", collected_at),
                        "collected_at": collected_at,
                    }
                )

        return articles


# Backward-compatible alias for existing imports.
Cryptoscrap = CryptoNewsScraper
