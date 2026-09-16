#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Tự động kích hoạt virtual environment nếu có
if [ -f "$DIR/.venv/bin/activate" ]; then
  source "$DIR/.venv/bin/activate"
fi

export AIRFLOW_HOME="$DIR/airflow_demo"
export AIRFLOW__CORE__DAGS_FOLDER="$DIR/airflow_demo/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

echo "=========================================================="
echo "  KHỞI ĐỘNG AIRFLOW STANDALONE (Demo Mode)"
echo "  Python      : $(which python3)"
echo "  Airflow     : $(which airflow)"
echo "  AIRFLOW_HOME: $AIRFLOW_HOME"
echo "  DAGs Folder : $AIRFLOW__CORE__DAGS_FOLDER"
echo "  Web UI      : http://localhost:8080"
echo "=========================================================="
echo "Lưu ý: Mật khẩu admin sẽ hiển thị bên dưới khi Airflow khởi động lần đầu."
echo ""

airflow standalone
# Đường dẫn Web UI: http://localhost:8080
# Username: admin
# Password: qWG7XMuYzxgAvGhq