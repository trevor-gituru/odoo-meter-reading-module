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
#   DB_NAME         Name of an EXISTING database to use (required)
#   ADMIN_PASSWORD  Odoo master password
#
# Optional:
#   AUTO_INIT       If "true", runs Odoo with -i to install modules into
#                    DB_NAME on this boot (first deploy only — see note
#                    below). Any other value or unset: skipped.
#   INIT_MODULES    Comma-separated modules to install when AUTO_INIT is
#                    true. Defaults to "base,meter_invoice".
# -----------------------------------------------------------------------------

: "${DB_HOST:?DB_HOST must be set}"
: "${DB_PORT:?DB_PORT must be set}"
: "${DB_USER:?DB_USER must be set}"
: "${DB_PASSWORD:?DB_PASSWORD must be set}"
: "${DB_NAME:?DB_NAME must be set}"
: "${ADMIN_PASSWORD:?ADMIN_PASSWORD must be set}"

INIT_MODULES="${INIT_MODULES:-base,meter_invoice}"

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

# Pin Odoo to a single, pre-existing database rather than letting it
# create/list/drop databases itself. Providers like Supabase route
# connections through a pooler whose role doesn't have CREATEDB, so
# Odoo's own database manager (which issues CREATE DATABASE) can't be
# used here — the database named below must already exist on the
# server, and Odoo will just initialize/use it in place.
db_name = ${DB_NAME}

# Restrict database selection to exactly this one database, and hide
# the database manager UI (New/Backup/Restore/Drop) entirely, since
# none of those operations would work against a role without
# CREATEDB rights anyway. This also closes off /web/database/manager
# as an unauthenticated attack surface.
dbfilter = ^${DB_NAME}$
list_db = False

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

# Build the extra args array conditionally so a normal boot (AUTO_INIT
# unset/false) runs Odoo with no -i flag at all, rather than passing an
# empty/blank argument.
extra_args=()
if [ "${AUTO_INIT:-false}" = "true" ]; then
  echo "AUTO_INIT=true: installing modules [${INIT_MODULES}] into ${DB_NAME} on this boot."
  extra_args+=(-i "${INIT_MODULES}")
else
  echo "AUTO_INIT not set to true: skipping module installation, starting normally."
fi

echo "Starting Odoo..."

# Start Odoo using the generated configuration. -d pins the target
# database explicitly (redundant with db_name above, but making it
# explicit on the command line too avoids any ambiguity about which
# database module init/upgrade runs against).
exec "$@" --config=/etc/odoo/odoo.conf -d "${DB_NAME}" "${extra_args[@]}"
