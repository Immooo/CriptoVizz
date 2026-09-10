"""Validate untrusted queue payloads before analysis or database writes."""

import math
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit

MAX_MESSAGE_BYTES = 64 * 1024


def validate_article(article, *, enriched=False):
    if not isinstance(article, dict):
        raise ValueError("article must be an object")
    for field, maximum in {
        "article_id": 64,
        "source": 120,
        "title": 500,
        "url": 1000,
        "summary": 5000,
    }.items():
        value = article.get(field, "" if field == "summary" else None)
        if not isinstance(value, str) or len(value) > maximum:
            raise ValueError(f"invalid {field}")
        if field != "summary" and not value.strip():
            raise ValueError(f"empty {field}")
    if not re.fullmatch(r"[a-f0-9]{64}", article["article_id"]):
        raise ValueError("invalid article_id")
    url = urlsplit(article["url"])
    if url.scheme not in {"http", "https"} or not url.hostname:
        raise ValueError("article URL must use HTTP(S)")
    for field in ("published_at", "collected_at"):
        value = article.get(field)
        if not isinstance(value, str) or len(value) > 40:
            raise ValueError(f"invalid {field}")
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError(f"{field} must include timezone")
        if not 1000 <= parsed.year <= 9998:
            raise ValueError(f"{field} outside MySQL range")
        try:
            parsed.astimezone(timezone.utc)
        except OverflowError as exc:
            raise ValueError(f"invalid {field}") from exc
    if enriched:
        score = article.get("sentiment_score")
        if type(score) not in (int, float) or not math.isfinite(score) or not -1 <= score <= 1:
            raise ValueError("invalid sentiment score")
        if article.get("sentiment_label") not in {"positive", "neutral", "negative"}:
            raise ValueError("invalid sentiment label")
        topics = article.get("topics")
        if not isinstance(topics, list) or not 1 <= len(topics) <= 20:
            raise ValueError("invalid topics")
        if any(not isinstance(t, str) or not re.fullmatch(r"[a-z0-9_]{1,80}", t) for t in topics):
            raise ValueError("invalid topic")
        if len(set(topics)) != len(topics):
            raise ValueError("duplicate topics")
    return article
