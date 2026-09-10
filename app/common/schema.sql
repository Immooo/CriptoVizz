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
