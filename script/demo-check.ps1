$ErrorActionPreference = "Stop"

Write-Host "`n=== Conteneurs ==="
docker compose ps

Write-Host "`n=== Queues RabbitMQ ==="
docker compose exec -T rabbitmq rabbitmqctl list_queues name messages_ready messages_unacknowledged consumers

Write-Host "`n=== Données MySQL ==="
$cvPython = @'
import os
import mysql.connector

database = mysql.connector.connect(
    host=os.environ["MYSQL_HOST"],
    port=int(os.environ.get("MYSQL_PORT", "3306")),
    user=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    database=os.environ["MYSQL_DATABASE"],
)
cursor = database.cursor()
cursor.execute("SELECT COUNT(*) FROM news_articles")
print("articles:", cursor.fetchone()[0])
cursor.execute("SELECT source, COUNT(*) FROM news_articles GROUP BY source ORDER BY COUNT(*) DESC")
print("articles par source:")
for source, count in cursor.fetchall():
    print(f"  {source}: {count}")
cursor.execute("SELECT sentiment_label, COUNT(*) FROM news_articles GROUP BY sentiment_label ORDER BY sentiment_label")
print("sentiments, sans double comptage par thème:")
for label, count in cursor.fetchall():
    print(f"  {label}: {count}")
cursor.close()
database.close()
'@
$cvPython | docker compose exec -T queue python -

Write-Host "`nGrafana   : http://localhost:3000/d/crypto-news-analytics/crypto-news-analytics"
Write-Host "RabbitMQ  : http://localhost:15672"
