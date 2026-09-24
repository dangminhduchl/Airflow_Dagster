#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Automatically activate the virtual environment if present
if [ -f "$DIR/.venv/bin/activate" ]; then
  source "$DIR/.venv/bin/activate"
fi

export AIRFLOW_HOME="$DIR/airflow_demo"
export AIRFLOW__CORE__DAGS_FOLDER="$DIR/airflow_demo/dags"
export AIRFLOW__CORE__PLUGINS_FOLDER="$DIR/airflow_demo/plugins"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
# Override the absolute paths in airflow.cfg so it runs on any machine
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="sqlite:///$DIR/airflow_demo/airflow.db"
export AIRFLOW__LOGGING__BASE_LOG_FOLDER="$DIR/airflow_demo/logs"
export AIRFLOW__LOGGING__DAG_PROCESSOR_CHILD_PROCESS_LOG_DIRECTORY="$DIR/airflow_demo/logs/dag_processor"

echo "=========================================================="
echo "  STARTING AIRFLOW STANDALONE (Demo Mode)"
echo "  Python      : $(which python3)"
echo "  Airflow     : $(which airflow)"
echo "  AIRFLOW_HOME: $AIRFLOW_HOME"
echo "  DAGs Folder : $AIRFLOW__CORE__DAGS_FOLDER"
echo "  Web UI      : http://localhost:8080"
echo "=========================================================="
echo "Note: The admin password will be shown below when Airflow starts for the first time."
echo ""

airflow standalone
# Web UI URL: http://localhost:8080
# Username: admin
# Password: qWG7XMuYzxgAvGhq