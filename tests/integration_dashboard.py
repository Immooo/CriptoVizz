"""Exercise dashboard SQL through Grafana using read-only synthetic CTEs.

Run from the repository root with Grafana available and credentials in .env.
No application records are inserted, modified or deleted.
"""

import base64
import json
import os
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = """WITH news_articles AS (
SELECT 'inside-start' AS title, 'Fixture' AS source, 'https://example.test/1' AS url,
CAST('2026-01-02 15:56:54' AS DATETIME) AS published_at,
CAST('2026-01-02 15:56:54' AS DATETIME) AS collected_at,
JSON_ARRAY('bitcoin') AS topics, 'positive' AS sentiment_label, 1 AS sentiment_score
UNION ALL SELECT 'inside-end', 'Fixture', 'https://example.test/2',
'2026-01-02 16:00:10', '2026-01-02 16:00:10', JSON_ARRAY('bitcoin'), 'negative', -1
UNION ALL SELECT 'outside-before', 'Fixture', 'https://example.test/3',
'2026-01-02 15:56:00', '2026-01-02 15:56:00', JSON_ARRAY('bitcoin'), 'neutral', 0
UNION ALL SELECT 'outside-after', 'Fixture', 'https://example.test/4',
'2026-01-02 16:02:00', '2026-01-02 16:02:00', JSON_ARRAY('bitcoin'), 'neutral', 0
), analytics_hourly AS (
SELECT CAST('2026-01-02 15:00:00' AS DATETIME) AS bucket_start,
'bitcoin' AS topic, 7 AS article_count, 2 AS sentiment_sum
), pipeline_hourly AS (
SELECT CAST('2026-01-02 15:00:00' AS DATETIME) AS bucket_start,
'Fixture' AS source, 2 AS article_count, 200 AS latency_sum_ms
) """


def epoch_ms(value):
    return int(datetime.fromisoformat(value).timestamp() * 1000)


def execute(panel, auth, start, end, topic="bitcoin", fixtures=True):
    query = dict(panel["targets"][0])
    query.update(datasource=panel["datasource"], intervalMs=60000, maxDataPoints=1000)
    query["rawSql"] = (FIXTURES if fixtures else "") + query["rawSql"].replace(
        "${topic:sqlstring}", "'" + topic + "'"
    )
    payload = {"from": str(start), "to": str(end), "queries": [query]}
    request = urllib.request.Request(
        os.getenv("GRAFANA_TEST_URL", "http://localhost:3000") + "/api/ds/query",
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)["results"]["A"]
    assert not result.get("error"), result.get("error")
    return result.get("frames", [])


def values(frames, field_type):
    return [
        value
        for frame in frames
        for field, column in zip(frame["schema"]["fields"], frame["data"]["values"])
        if field["type"] == field_type
        for value in column
        if value is not None
    ]


def main():
    config = dict(
        line.split("=", 1)
        for line in (ROOT / ".env").read_text().splitlines()
        if "=" in line and not line.startswith("#")
    )
    auth = base64.b64encode(("admin:" + config["GRAFANA_ADMIN_PASSWORD"]).encode()).decode()
    panels = json.loads((ROOT / "grafana/dashboards/crypto-news.json").read_text())["panels"]
    start = epoch_ms("2026-01-02T15:56:30+00:00")
    end = epoch_ms("2026-01-02T16:01:30+00:00")
    for panel in panels:
        frames = execute(panel, auth, start, end)
        timestamps = values(frames, "time")
        if panel["type"] == "timeseries":
            assert timestamps and all(start <= t <= end for t in timestamps), panel["title"]
        if panel["id"] in (1, 3, 5):
            assert sum(values(frames, "number")) == 2, panel["title"]
        if panel["id"] in (7, 8, 9):
            expected = {7: 2, 8: 1, 9: 0}[panel["id"]]
            assert values(frames, "number") == [expected], panel["title"]
        if panel["id"] == 4:
            strings = values(frames, "string")
            assert "inside-start" in strings and "inside-end" in strings, strings
            assert "outside-before" not in strings and "outside-after" not in strings, strings
        if panel["id"] in (1, 2, 3, 4):
            assert not values(execute(panel, auth, start, end, "ethereum"), "number")
            assert not values(execute(panel, auth, start, end, "ethereum"), "string")
        print("PASS five-minute range:", panel["title"])
    long_frames = execute(
        next(panel for panel in panels if panel["id"] == 1),
        auth,
        epoch_ms("2026-01-01T00:00:00+00:00"),
        epoch_ms("2026-01-03T00:00:00+00:00"),
    )
    assert sum(values(long_frames, "number")) == 7, "historical aggregates were lost"
    print("PASS long range: retained hourly aggregates")
    import time

    now = int(time.time() * 1000)
    for hours in (1 / 12, 1, 6, 48):
        for panel in panels:
            execute(panel, auth, now - int(hours * 3600000), now, fixtures=False)
        print(f"PASS real database schema: {hours:g}-hour range")


if __name__ == "__main__":
    main()
