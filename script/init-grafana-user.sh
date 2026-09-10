#!/bin/sh
# MySQL sources non-executable init scripts on Linux. Keep shell options local.
(
set -eu
# Hex-only generated secrets avoid SQL interpolation and Compose escaping hazards.
case "$GRAFANA_DB_PASSWORD" in *[!a-fA-F0-9]*|"") echo "GRAFANA_DB_PASSWORD must be hexadecimal" >&2; exit 1;; esac
case "$MYSQL_DATABASE" in *[!a-zA-Z0-9_]*|"") echo "Invalid MYSQL_DATABASE" >&2; exit 1;; esac
MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot <<SQL
CREATE USER IF NOT EXISTS 'grafana_reader'@'%' IDENTIFIED BY '$GRAFANA_DB_PASSWORD';
ALTER USER 'grafana_reader'@'%' IDENTIFIED BY '$GRAFANA_DB_PASSWORD';
GRANT SELECT ON \`$MYSQL_DATABASE\`.* TO 'grafana_reader'@'%';
SQL
)
