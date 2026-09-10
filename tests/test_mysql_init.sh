#!/usr/bin/env bash
# Match MySQL entrypoint behavior: source a non-executable initializer.
set -eo pipefail
export GRAFANA_DB_PASSWORD=abcdef MYSQL_DATABASE=crypto MYSQL_ROOT_PASSWORD=test
mysql() { cat > /dev/null; }
initial_options="$-"
. script/init-grafana-user.sh
if [[ "$-" != "$initial_options" ]]; then
    echo "FAIL: initializer changed parent shell options" >&2
    exit 1
fi
# MySQL's entrypoint legitimately reads an unset positional parameter.
check_optional_argument() { test -z "$1"; }
check_optional_argument
if (export GRAFANA_DB_PASSWORD=invalid-secret; . script/init-grafana-user.sh); then
    echo "FAIL: initializer accepted an invalid secret" >&2
    exit 1
fi
echo "PASS: sourced initializer preserves shell options and rejects invalid secrets"
