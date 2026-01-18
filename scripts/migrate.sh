#!/usr/bin/env bash
set -euo pipefail

compose_cmd="docker compose"
reset_db="false"

if [ "${1:-}" = "--reset-db" ]; then
  reset_db="true"
  shift
fi

migration_message="${*:-auto migration}"

if [ "${reset_db}" = "true" ]; then
  ${compose_cmd} down -v
  rm -f migrations/versions/*.py
fi

db_container_id="$(${compose_cmd} ps -q db)"
db_running="false"
started_db="false"

if [ -n "${db_container_id}" ]; then
  db_status="$(docker inspect -f '{{.State.Status}}' "${db_container_id}")"
  if [ "${db_status}" = "running" ]; then
    db_running="true"
  fi
fi

if [ "${db_running}" = "false" ]; then
  ${compose_cmd} up -d db
  started_db="true"
fi

db_container_id="$(${compose_cmd} ps -q db)"
for _ in $(seq 1 30); do
  db_health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "${db_container_id}")"
  if [ "${db_health}" = "healthy" ]; then
    break
  fi
  sleep 2
done

db_health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "${db_container_id}")"
if [ "${db_health}" != "healthy" ]; then
  echo "database is not healthy"
  exit 1
fi

${compose_cmd} run --rm migrator alembic upgrade head
${compose_cmd} run --rm migrator alembic revision --autogenerate -m "${migration_message}"
${compose_cmd} run --rm migrator alembic upgrade head

if [ "${started_db}" = "true" ]; then
  ${compose_cmd} stop db
fi
