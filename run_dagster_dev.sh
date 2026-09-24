#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Automatically activate the virtual environment if present
if [ -f "$DIR/.venv/bin/activate" ]; then
  source "$DIR/.venv/bin/activate"
fi

cd "$DIR/dagster_demo"

echo "=========================================================="
echo "  STARTING DAGSTER DEV SERVER (Ops & Assets)"
echo "  Python  : $(which python3)"
echo "  Dagster : $(which dagster)"
echo "  Web UI  : http://localhost:3000"
echo "=========================================================="
echo ""

dagster dev -f definitions.py
