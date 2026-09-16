#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Tự động kích hoạt virtual environment nếu có
if [ -f "$DIR/.venv/bin/activate" ]; then
  source "$DIR/.venv/bin/activate"
fi

cd "$DIR/dagster_demo"

echo "=========================================================="
echo "  KHỞI ĐỘNG DAGSTER DEV SERVER (Ops & Assets)"
echo "  Python  : $(which python3)"
echo "  Dagster : $(which dagster)"
echo "  Web UI  : http://localhost:3000"
echo "=========================================================="
echo ""

dagster dev -f definitions.py
