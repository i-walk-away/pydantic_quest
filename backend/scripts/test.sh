#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f ".env.test" ]]; then
  echo "Missing .env.test. Create it or export required env vars before running tests." >&2
  exit 1
fi

set -a
source ".env.test"
set +a

uv run pytest
