#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$ROOT/build"
PYTEST_TMP="$BUILD/pytest_tmp"
mkdir -p "$PYTEST_TMP"
export TMPDIR="$PYTEST_TMP"
export PYTHONPATH="$ROOT/src"
"$ROOT/.venv/bin/python" -m pytest --basetemp="$PYTEST_TMP" -q
