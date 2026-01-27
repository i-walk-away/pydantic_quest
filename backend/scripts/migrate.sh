#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "${script_dir}/../.." && pwd)"
backend_root="${project_root}/backend"
compose_cmd="docker compose --project-directory ${project_root}"
reset_db="false"
versions_dir="${backend_root}/migrations/versions"
started_db="false"
env_file="${project_root}/.env"
python_cmd=""

if [ ! -f "${env_file}" ]; then
  echo "env file ${env_file} not found"
  exit 1
fi

set -a
# shellcheck disable=SC1090
. "${env_file}"
set +a

if command -v python >/dev/null 2>&1; then
  python_cmd="python"
elif command -v python3 >/dev/null 2>&1; then
  python_cmd="python3"
else
  echo "python interpreter not found"
  exit 1
fi

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
deleted_revision="false"

if [ -d "${versions_dir}" ]; then
  latest_before="$(ls -t "${versions_dir}"/*.py 2>/dev/null | head -n 1 || true)"
fi

${compose_cmd} run --rm migrator alembic revision --autogenerate -m "${migration_message}"

if [ -d "${versions_dir}" ]; then
  latest_after="$(ls -t "${versions_dir}"/*.py 2>/dev/null | head -n 1 || true)"
fi

if [ -n "${latest_after}" ] && [ "${latest_after}" != "${latest_before}" ]; then
  is_empty_revision="$(
    "${python_cmd}" - "${latest_after}" <<'PY'
import ast
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
tree = ast.parse(path.read_text(encoding="utf-8"))

def is_noop(func_name: str) -> bool:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            body = [item for item in node.body if not isinstance(item, ast.Expr)]
            return len(body) == 1 and isinstance(body[0], ast.Pass)
    return False

has_ops = any(
    isinstance(node, ast.Attribute) and getattr(node.value, "id", None) == "op"
    for node in ast.walk(tree)
)
print("true" if is_noop(func_name="upgrade") and is_noop(func_name="downgrade") and not has_ops else "false")
PY
  )"

  if [ "${is_empty_revision}" = "true" ]; then
    rm -f "${latest_after}"
    deleted_revision="true"
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
