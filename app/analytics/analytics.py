import re
from collections import Counter


POSITIVE_WORDS = {
    "adoption", "approval", "approved", "bull", "bullish", "gain", "gains",
    "growth", "high", "launch", "profit", "rally", "record", "rise", "surge",
}
NEGATIVE_WORDS = {
    "attack", "ban", "bear", "bearish", "crash", "crime", "decline", "drop",
    "fraud", "hack", "loss", "lawsuit", "risk", "scam", "selloff", "warning",
}
TOPICS = {
    "bitcoin": {"bitcoin", "btc"},
    "ethereum": {"ethereum", "ether", "eth"},
    "regulation": {"law", "lawsuit", "regulation", "regulator", "sec", "policy"},
    "defi": {"defi", "decentralized", "lending", "staking"},
    "security": {"attack", "exploit", "hack", "scam", "security"},
    "markets": {"bull", "bear", "etf", "market", "price", "trading"},
}


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def analyze_article(article):
    words = tokenize(f"{article.get('title', '')} {article.get('summary', '')}")
    counts = Counter(words)
    positive = sum(counts[word] for word in POSITIVE_WORDS)
    negative = sum(counts[word] for word in NEGATIVE_WORDS)
    score = max(-1.0, min(1.0, (positive - negative) / max(positive + negative, 1)))
    label = "positive" if score > 0 else "negative" if score < 0 else "neutral"

    topics = [
        topic for topic, keywords in TOPICS.items() if any(counts[word] for word in keywords)
    ]

    return {
        **article,
        "sentiment_score": score,
        "sentiment_label": label,
        "topics": topics or ["other"],
    }
