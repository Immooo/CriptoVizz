import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1] / "app" / "analytics"))

from analytics import analyze_article  # noqa: E402


class AnalyticsTests(unittest.TestCase):
    def test_positive_bitcoin_article(self):
        result = analyze_article(
            {"title": "Bitcoin adoption gains as market rallies", "summary": ""}
        )
        self.assertEqual(result["sentiment_label"], "positive")
        self.assertGreater(result["sentiment_score"], 0)
        self.assertIn("bitcoin", result["topics"])
        self.assertIn("markets", result["topics"])

    def test_negative_security_article(self):
        result = analyze_article(
            {"title": "Crypto exchange hack warning", "summary": "Attack risk rises"}
        )
        self.assertEqual(result["sentiment_label"], "negative")
        self.assertIn("security", result["topics"])

    def test_unknown_topic_is_other(self):
        result = analyze_article({"title": "Community conference", "summary": ""})
        self.assertEqual(result["sentiment_label"], "neutral")
        self.assertEqual(result["topics"], ["other"])


if __name__ == "__main__":
    unittest.main()
