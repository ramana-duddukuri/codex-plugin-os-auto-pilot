#!/bin/bash
set -e

# Change to script directory
cd "$(dirname "$0")"

# Prefer python3 or python
if command -v python3 >/dev/null 2>&1; then
    python3 scripts/setup.py "$@"
elif command -v python >/dev/null 2>&1; then
    python scripts/setup.py "$@"
else
    echo "❌ Error: Python 3.10+ is required but not found on PATH."
    exit 1
fi
