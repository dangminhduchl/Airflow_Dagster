# Airflow vs. Dagster: Multi-Page Invoice PDF Demo

The same business pipeline — processing a multi-page invoice PDF and running a financial audit — implemented twice:

- **Apache Airflow** (task-driven): `@task.branch` routing and dynamic task mapping (`.expand()`).
- **Dagster** (asset-driven): Software-Defined Assets with `@asset_check` validations.

Both use identical input data, checks, and results, so you can compare the two approaches side by side.

## Project structure

```text
.
├── README.md
├── requirements.txt                  # Pinned dependencies (Airflow, Dagster, pytest)
├── run_airflow_standalone.sh         # Start Airflow UI on port 8080
├── run_dagster_dev.sh                # Start Dagster UI on port 3000
├── airflow_demo/
│   ├── airflow.cfg                   # Airflow config (paths are overridden by the run script)
│   └── dags/
│       └── invoice_multipage_pdf_dag.py
└── dagster_demo/
    ├── definitions.py                # Dagster entry point
    ├── invoice_processing/
    │   ├── __init__.py
    │   └── assets.py                 # Assets + 3 asset checks
    └── tests/
        └── test_invoice_processing.py
```

## The pipeline

The input `march_input_documents.pdf` (simulated) has 4 pages:

1. VAT invoice — 50,000,000 + 5,000,000 VAT = 55,000,000 VND
2. Electricity bill (EVN) — 1,850,000 VND
3. Business travel flight ticket — 3,200,000 VND
4. Retail receipt without a tax code — 150,000 VND (not tax-deductible)

Pages are classified into 4 categories, extracted in parallel, collected, and audited by 3 checks:

- **Check 1:** the PDF is valid and has more than 0 pages.
- **Check 2:** VAT math is correct (Total == Subtotal + VAT).
- **Check 3 (blocking):** total expense ≤ 100,000,000 VND and no negative amounts.

Expected ledger result: total expense **60,200,000 VND**, deductible VAT **5,000,000 VND**.

## Requirements

- macOS or Linux (on Windows, use WSL)
- Python 3.14 (the version this project was built and tested with)
- [uv](https://docs.astral.sh/uv/) (recommended) or `pip`

## Installation

Using **uv**:

```bash
uv venv --python 3.14 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Or using **pip**:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The run scripts activate `.venv` automatically if it exists, so the virtual environment must be named `.venv` in the project root.

## Running Dagster

```bash
./run_dagster_dev.sh
```

Open http://localhost:3000, then:

1. Go to **Assets** to see the lineage graph (4 parallel branches fanning into `categorized_invoices`).
2. Click **Materialize all** to run the pipeline.
3. Open an asset's **Checks** tab to see the 3 asset checks and their metadata.

## Running Airflow

```bash
./run_airflow_standalone.sh
```

On first start, Airflow initializes its database and prints a generated password for the `admin` user in the terminal. It is also saved to `airflow_demo/simple_auth_manager_passwords.json.generated`.

Open http://localhost:8080, log in as `admin`, then:

1. Find the DAG `invoice_multipage_pdf_airflow_dag` and unpause it.
2. Click **Trigger** to start a run.
3. Open the **Graph** view to see the file-integrity branch, the 4 mapped extraction branches, and the audit branch.

The script sets `AIRFLOW_HOME` to `airflow_demo/`, so the database (`airflow.db`) and logs are stored there.

## Running the tests

```bash
source .venv/bin/activate
PYTHONPATH=. pytest dagster_demo/tests -v
```

All 4 tests should pass: the full asset materialization and one test for each check.

## Troubleshooting

- **Port already in use:** stop the other process on port 3000 or 8080, or stop a previous run with `Ctrl+C`.
- **`airflow` / `dagster`: command not found:** the virtual environment isn't set up; repeat the installation steps.
- **Reset Airflow state:** stop Airflow, delete `airflow_demo/airflow.db`, `airflow_demo/logs/`, and `airflow_demo/simple_auth_manager_passwords.json.generated`, then start it again. A new admin password will be generated.
