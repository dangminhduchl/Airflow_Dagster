#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$DIR/.venv/bin:$PATH"
cd "$DIR/dagster_demo"

echo "=========================================================="
echo "  KHỞI ĐỘNG DAGSTER DEV SERVER (Ops & Assets)"
echo "  Web UI: http://localhost:3000"
echo "=========================================================="
echo ""
"$DIR/.venv/bin/dagster" dev -m order_processing
