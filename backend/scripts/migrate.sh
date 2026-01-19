#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_dir}/.." && pwd)"
backend_root="${project_root}/backend"
compose_cmd="docker compose --project-directory ${project_root}"
reset_db="false"
versions_dir="${backend_root}/migrations/versions"
started_db="false"

if [ "${1:-}" = "--reset-db" ]; then
  reset_db="true"
  shift
fi

migration_message="${*:-auto migration}"

if [ "${reset_db}" = "true" ]; then
  ${compose_cmd} down -v
  rm -f "${versions_dir}"/*.py
  mkdir -p "${versions_dir}"
fi

db_container_id="$(${compose_cmd} ps -q db)"
db_running="false"

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

if [ "${reset_db}" != "true" ]; then
  ${compose_cmd} run --rm migrator alembic upgrade head
fi

latest_before=""
latest_after=""
revision_created="false"

if [ -d "${versions_dir}" ]; then
  latest_before="$(ls -t "${versions_dir}"/*.py 2>/dev/null | head -n 1 || true)"
fi

${compose_cmd} run --rm migrator alembic revision --autogenerate -m "${migration_message}"

if [ -d "${versions_dir}" ]; then
  latest_after="$(ls -t "${versions_dir}"/*.py 2>/dev/null | head -n 1 || true)"
fi

if [ -n "${latest_after}" ] && [ "${latest_after}" != "${latest_before}" ]; then
  is_empty_revision="$(
    python - "${latest_after}" <<'PY'
import ast
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
tree = ast.parse(path.read_text(encoding="utf-8"))

def is_pass(func_name: str) -> bool:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return len(node.body) == 1 and isinstance(node.body[0], ast.Pass)
    return False

print("true" if is_pass(func_name="upgrade") and is_pass(func_name="downgrade") else "false")
PY
  )"

  if [ "${is_empty_revision}" = "true" ]; then
    rm -f "${latest_after}"
  else
    revision_created="true"
  fi
fi

if [ "${revision_created}" = "true" ]; then
  ${compose_cmd} run --rm migrator alembic upgrade head
fi

if [ "${started_db}" = "true" ]; then
  ${compose_cmd} stop db
fi
