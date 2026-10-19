#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://127.0.0.1:8000}"

echo "Checking API health at ${API_URL}/health ..."
curl --fail --silent --show-error "${API_URL}/health"
echo
