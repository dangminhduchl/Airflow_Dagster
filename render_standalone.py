import subprocess
import os

html_airflow = """<!DOCTYPE html>
<html>
<head>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  body { background: #071322; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; }
  .mermaid text { font-family: 'Segoe UI', Arial, sans-serif !important; font-weight: 600 !important; }
</style>
</head>
<body>
<div class="mermaid">
flowchart LR
    T1["📄 ingest_pdf<br/><i>(4-Page PDF)</i>"] --> T2{"⚙️ check_pdf<br/><i>@task.branch</i>"}
    T2 -- "Lỗi" --> T_err["⚠️ error_stop<br/><i>(Hard Stop)</i>"]
    T2 -- "Hợp lệ" --> T_split["✂️ classify"]

    T_split --> P1["⚡ vat (55M)"]
    T_split --> P2["⚡ util (1.85M)"]
    T_split --> P3["⚡ reimb (3.2M)"]
    T_split --> P4["⚡ invalid (150K ⚠️)"]

    P1 & P2 & P3 & P4 --> T_collect["📥 collect_invoices<br/><i>(TriggerRule)</i>"]
    T_collect --> T_audit{"🔍 audit_budget<br/><i>(<= 100M)</i>"}
    T_audit -- "Pass" --> T_pass["✅ lock_ledger<br/><i>(60.2M -> SAP)</i>"]
    T_audit -- "Fail" --> T_alert["🚨 alert_violation"]

    style T1 fill:#0f2744,stroke:#38bdf8,stroke-width:2px,color:#f0f9ff
    style T2 fill:#451a03,stroke:#f59e0b,stroke-width:2px,color:#fef08a
    style T_err fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#fca5a5
    style T_split fill:#0f2744,stroke:#60a5fa,color:#f0f9ff
    style P1 fill:#091e36,stroke:#38bdf8,color:#38bdf8
    style P2 fill:#091e36,stroke:#38bdf8,color:#38bdf8
    style P3 fill:#091e36,stroke:#38bdf8,color:#38bdf8
    style P4 fill:#2e0b16,stroke:#f43f5e,color:#fecdd3
    style T_collect fill:#112a4d,stroke:#0284c7,color:#e0f2fe
    style T_audit fill:#451a03,stroke:#f59e0b,stroke-width:2px,color:#fef08a
    style T_pass fill:#064e3b,stroke:#10b981,stroke-width:2.5px,color:#86efac
    style T_alert fill:#450a0a,stroke:#ef4444,stroke-width:2.5px,color:#fca5a5
</div>
<script>mermaid.initialize({startOnLoad:true, theme:'dark'});</script>
</body>
</html>"""

html_dagster = """<!DOCTYPE html>
<html>
<head>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  body { background: #041a1d; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; }
  .mermaid text { font-family: 'Segoe UI', Arial, sans-serif !important; font-weight: 600 !important; }
</style>
</head>
<body>
<div class="mermaid">
flowchart LR
    C1{{"🛡️ check_integrity"}} -. "Bảo vệ" .-> A1[("📄 raw_multipage_pdf<br/><i>(File thô 4 trang)</i>")]
    A1 ==>|"I/O Manager"| A2[("📑 extracted_pages<br/><i>(OCR & AI Parser)</i>")]

    A2 ==> V1[("⚡ vat_invoices<br/><i>(55M)</i>")]
    A2 ==> V2[("⚡ utility_invoices<br/><i>(1.85M)</i>")]
    A2 ==> V3[("⚡ reimbursement<br/><i>(3.2M)</i>")]
    A2 ==> V4[("⚡ invalid_invoices<br/><i>(150K ⚠️)</i>")]

    V1 & V2 & V3 & V4 ==> A3[("📊 categorized_invoices<br/><i>(Tổng: 60.2M)</i>")]
    C2{{"🛡️ check_tax"}} -. "Kiểm tra" .-> A3
    C3{{"🛡️ check_budget<br/><i>BLOCKING ⛔</i>"}} -. "Ngắt cầu dao" .-> A3
    A3 ==>|"Check 3 = PASS"| A4[("💎 monthly_financial_expense_ledger<br/><i>(Approved: 60.2M -> SAP ERP)</i>")]

    style A1 fill:#082e33,stroke:#14b8a6,stroke-width:2px,color:#ffffff
    style A2 fill:#082e33,stroke:#14b8a6,stroke-width:2px,color:#ffffff
    style V1 fill:#0a373d,stroke:#24d39e,color:#f0fdfa
    style V2 fill:#0a373d,stroke:#24d39e,color:#f0fdfa
    style V3 fill:#0a373d,stroke:#24d39e,color:#f0fdfa
    style V4 fill:#2e0b16,stroke:#f43f5e,color:#fecdd3
    style A3 fill:#0a3c42,stroke:#00e599,stroke-width:2px,color:#ffffff
    style A4 fill:#064e3b,stroke:#00e599,stroke-width:3px,color:#ffffff
    style C1 fill:#042125,stroke:#2dd4bf,color:#5eead4
    style C2 fill:#042125,stroke:#2dd4bf,color:#5eead4
    style C3 fill:#450a0a,stroke:#ef4444,stroke-width:2.5px,color:#fca5a5
</div>
<script>mermaid.initialize({startOnLoad:true, theme:'dark'});</script>
</body>
</html>"""

with open("temp_af.html", "w") as f:
    f.write(html_airflow)
with open("temp_dg.html", "w") as f:
    f.write(html_dagster)

cwd = os.getcwd()
subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--virtual-time-budget=3000", "--window-size=2200,600", "--screenshot=airflow_horizontal.png", f"file://{cwd}/temp_af.html"])
subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--virtual-time-budget=3000", "--window-size=2200,600", "--screenshot=dagster_horizontal.png", f"file://{cwd}/temp_dg.html"])

print("Generated airflow_horizontal.png and dagster_horizontal.png successfully!")
