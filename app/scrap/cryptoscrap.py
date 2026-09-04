import hashlib
import os
from datetime import datetime, timezone

import feedparser


DEFAULT_FEEDS = (
    "https://www.coindesk.com/arc/outboundfeeds/rss/,"
    "https://cointelegraph.com/rss"
)


class CryptoNewsScraper:
    """Collect and normalize articles from cryptocurrency RSS feeds."""

    def __init__(self, feed_urls=None):
        configured = feed_urls or os.getenv("NEWS_FEED_URLS", DEFAULT_FEEDS).split(",")
        self.feed_urls = [url.strip() for url in configured if url.strip()]

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
            feed = feedparser.parse(feed_url)
            if feed.bozo and not feed.entries:
                print(f"Unable to read RSS feed {feed_url}: {feed.bozo_exception}")
                continue

            source = feed.feed.get("title", feed_url)
            for entry in feed.entries:
                url = entry.get("link") or entry.get("id")
                title = (entry.get("title") or "").strip()
                if not url or not title:
                    continue

                articles.append(
                    {
                        "article_id": self._article_id(url),
                        "source": source[:120],
                        "title": title[:500],
                        "summary": (entry.get("summary") or "")[:5000],
                        "url": url[:1000],
                        "published_at": self._iso_datetime(
                            entry, "published_parsed", collected_at
                        ),
                        "collected_at": collected_at,
                    }
                )

        return articles


# Backward-compatible alias for existing imports.
Cryptoscrap = CryptoNewsScraper
