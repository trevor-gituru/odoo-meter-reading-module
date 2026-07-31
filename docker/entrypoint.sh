#!/bin/bash
set -e

# -----------------------------------------------------------------------------
# Generate the Odoo configuration file from runtime environment variables.
#
# Expected environment variables:
#   DB_HOST         PostgreSQL host
#   DB_PORT         PostgreSQL port
#   DB_USER         PostgreSQL username
#   DB_PASSWORD     PostgreSQL password
#   ADMIN_PASSWORD  Odoo master password
# -----------------------------------------------------------------------------

: "${DB_HOST:?DB_HOST must be set}"
: "${DB_PORT:?DB_PORT must be set}"
: "${DB_USER:?DB_USER must be set}"
: "${DB_PASSWORD:?DB_PASSWORD must be set}"
: "${ADMIN_PASSWORD:?ADMIN_PASSWORD must be set}"

mkdir -p /etc/odoo

cat >/etc/odoo/odoo.conf <<EOF
[options]

# Core Odoo addons plus custom addons.
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons

# PostgreSQL connection.
db_host = ${DB_HOST}
db_port = ${DB_PORT}
db_user = ${DB_USER}
db_password = ${DB_PASSWORD}

# Odoo master password used for database management.
admin_passwd = ${ADMIN_PASSWORD}

# Enable proxy mode when running behind a reverse proxy.
proxy_mode = True
EOF

echo "Generated Odoo configuration (secrets redacted):"
grep -v -E "^(db_password|admin_passwd)[[:space:]]*=" /etc/odoo/odoo.conf

# -----------------------------------------------------------------------------
# Wait for PostgreSQL to accept TCP connections before starting Odoo.
#
# A healthcheck-gated `depends_on` in docker-compose only guarantees
# Postgres was ready at container *start*, not that it stays reachable
# through the moment Odoo tries to connect, and there's no such guarantee
# at all if this image runs outside Compose (e.g. `docker run`, or a PaaS
# without native healthcheck ordering). Odoo doesn't retry gracefully on
# its own first-boot connection attempt, so we retry here instead.
# -----------------------------------------------------------------------------
echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
attempt=0
max_attempts=30
until (exec 3<>"/dev/tcp/${DB_HOST}/${DB_PORT}") 2>/dev/null; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge "$max_attempts" ]; then
    echo "ERROR: PostgreSQL did not become reachable after ${max_attempts} attempts. Exiting."
    exit 1
  fi
  echo "PostgreSQL not reachable yet (attempt ${attempt}/${max_attempts}), retrying in 2s..."
  sleep 2
done
echo "PostgreSQL is reachable."

echo "Starting Odoo..."

# Start Odoo using the generated configuration.
exec "$@" --config=/etc/odoo/odoo.conf
