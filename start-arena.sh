#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v uv >/dev/null || { echo 'Install uv: https://docs.astral.sh/uv/'; exit 1; }
command -v npm >/dev/null || { echo 'Install Node.js 22 or newer: https://nodejs.org/'; exit 1; }
uv sync --frozen --extra dev
npm ci
npm run build
if [[ "${1:-}" == "--prepare" ]]; then
  shift
  uv run python -m arena.setup --models "${@:-laya}"
fi
echo 'Jev Arena: http://127.0.0.1:8787 — keep this terminal open.'
exec uv run uvicorn arena.api:app --host 127.0.0.1 --port 8787
