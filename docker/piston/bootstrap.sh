#!/bin/sh
set -eu

node /opt/piston/install-runtime.js

exec /piston_api/src/docker-entrypoint.sh
