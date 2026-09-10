"""Create a local configuration with random secrets; never overwrite an existing file."""

import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
content = (root / ".env.example").read_text(encoding="utf-8")
for key in (
    "MYSQL_PASSWORD",
    "MYSQL_ROOT_PASSWORD",
    "GRAFANA_ADMIN_PASSWORD",
    "GRAFANA_DB_PASSWORD",
    "RABBITMQ_PASSWORD",
):
    lines = content.splitlines()
    content = (
        "\n".join(
            key + "=" + secrets.token_hex(24) if line.startswith(key + "=") else line
            for line in lines
        )
        + "\n"
    )
with (root / ".env").open("x", encoding="utf-8") as target:
    target.write(content)
print("Created .env. Keep this file private.")
