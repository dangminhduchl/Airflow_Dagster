"""
Multi-Page Invoice PDF Processing Workflow (Apache Airflow)
CLEARLY SHOWS 4 PARALLEL BRANCHES IN THE GRAPH VIEW UI:
1. Ingest Multi-Page PDF: Load the combined PDF file (4 pages)
2. Check 1 (@task.branch): Verify the integrity of the PDF file
3. AI Classification & 4 Parallel Branches (.expand):
   - Branch 1: extract_vat_invoice (Extract tax code 0101234567, subtotal 50M + VAT 5M = 55M)
   - Branch 2: extract_utility_invoice (Extract customer code PE0100098765, electricity bill 1.85M)
   - Branch 3: extract_reimbursement_invoice (Extract employee ID NV-889, flight ticket 3.2M)
   - Branch 4: extract_invalid_invoice (Warn that 150k is not tax-deductible)
4. Check 2 & 3 (@task.branch - Financial Audit):
   - Verify the tax formula (Total = Subtotal + VAT)
   - Verify the budget limit (Total expense <= 100 million VND)
   - If PASS -> Lock the accounting ledger (lock_and_publish_financial_ledger)
   - If VIOLATED -> Branch to the audit alert (alert_financial_audit_violation)
"""
from datetime import datetime
from typing import List, Dict, Any

from airflow.sdk import dag, task
from airflow.task.trigger_rule import TriggerRule
from airflow.providers.standard.operators.empty import EmptyOperator


# -------------------------------------------------------------
# 1. INGEST MULTI-PAGE PDF
# -------------------------------------------------------------
@task
def ingest_multipage_invoice_pdf() -> Dict[str, Any]:
    """Simulate loading a combined PDF file containing multiple invoice pages (100% same data as Dagster)."""
    return {
        "pdf_filename": "march_input_documents.pdf",
        "is_valid": True,
        "total_pages": 4,
        "pages": [
            {
                "page_num": 1,
                "raw_text": "VALUE-ADDED TAX (VAT) INVOICE\nForm No.: 01GTKT0/001\nSeller tax code: 0101234567\nAmount before tax: 50,000,000 VND\nVAT (10%): 5,000,000 VND\nTotal payment: 55,000,000 VND",
            },
            {
                "page_num": 2,
                "raw_text": "OFFICE ELECTRICITY BILL (EVN)\nCustomer code: PE0100098765\nPrevious reading: 1450 - Current reading: 1890\nBilling period: March 2026\nTotal payment: 1,850,000 VND",
            },
            {
                "page_num": 3,
                "raw_text": "BUSINESS TRAVEL INVOICE - FLIGHT TICKET\nEmployee: Nguyen Van A (Employee ID: NV-889)\nRoute: Hanoi - Ho Chi Minh City\nPurpose: Meeting with a client partner\nTotal amount: 3,200,000 VND",
            },
            {
                "page_num": 4,
                "raw_text": "RETAIL PAYMENT RECEIPT (NO TAX CODE)\nOffice convenience store\nDescription: Tea and coffee for guests\nTotal amount: 150,000 VND",
            },
        ],
    }


# -------------------------------------------------------------
# 2. CHECK 1 (@task.branch): Verify file integrity
# -------------------------------------------------------------
@task.branch
def check_pdf_integrity(pdf_data: Dict[str, Any]) -> str:
    """File-level check: valid, or empty/corrupted."""
    is_valid = pdf_data.get("is_valid", False)
    pages = pdf_data.get("pages", [])

    if is_valid and len(pages) > 0:
        print(f"[CHECK 1 PASS] File '{pdf_data.get('pdf_filename')}' is valid ({len(pages)} pages). Continuing extraction.")
        return "classify_invoice_pages"
    else:
        print("[CHECK 1 FAIL] File is corrupted or empty. Taking the skip branch.")
        return "handle_corrupted_pdf_file"


@task
def handle_corrupted_pdf_file():
    print("[ALERT] Invalid PDF file. Processing has been stopped.")
    return {"status": "CORRUPTED_OR_EMPTY"}


# -------------------------------------------------------------
# 3. AI CLASSIFICATION INTO 4 INVOICE GROUPS
# -------------------------------------------------------------
@task
def classify_invoice_pages(pdf_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Classify into 4 groups: VAT, Utility, Travel reimbursement, Receipt."""
    groups = {
        "vat_invoices": [],
        "utility_invoices": [],
        "reimbursement_invoices": [],
        "invalid_invoices": [],
    }

    for page in pdf_data["pages"]:
        text = page["raw_text"].upper()

        if "VALUE-ADDED TAX" in text or "GTKT" in text:
            groups["vat_invoices"].append({**page, "type": "VAT_INVOICE"})
        elif "ELECTRICITY" in text or "EVN" in text or "WATER" in text:
            groups["utility_invoices"].append({**page, "type": "UTILITY_INVOICE"})
        elif "BUSINESS TRAVEL" in text or "FLIGHT TICKET" in text:
            groups["reimbursement_invoices"].append({**page, "type": "REIMBURSEMENT_INVOICE"})
        else:
            groups["invalid_invoices"].append({**page, "type": "INVALID_RECEIPT"})

    print(f"[AI CLASSIFIER] Classification succeeded: VAT={len(groups['vat_invoices'])}, Utility={len(groups['utility_invoices'])}, Reimbursement={len(groups['reimbursement_invoices'])}, Invalid={len(groups['invalid_invoices'])}")
    return groups


# -------------------------------------------------------------
# 4. 4 SPECIALIZED BRANCH TASKS (CLEARLY VISIBLE IN GRAPH VIEW)
# -------------------------------------------------------------
@task
def extract_vat_invoice(page: Dict[str, Any]) -> Dict[str, Any]:
    print(f"-> [VAT extraction worker] Page {page['page_num']}...")
    return {
        "page_num": page["page_num"],
        "category": "VAT_INVOICE",
        "tax_code": "0101234567",
        "subtotal": 50000000,
        "vat_amount": 5000000,
        "total_amount": 55000000,
        "is_deductible": True,
        "status": "PROCESSED_TAX_MODULE",
    }


@task
def extract_utility_invoice(page: Dict[str, Any]) -> Dict[str, Any]:
    print(f"-> [Electricity extraction worker] Page {page['page_num']}...")
    return {
        "page_num": page["page_num"],
        "category": "UTILITY_INVOICE",
        "customer_code": "PE0100098765",
        "service_provider": "EVN",
        "billing_period": "03/2026",
        "total_amount": 1850000,
        "is_deductible": True,
        "status": "PROCESSED_OPEX_MODULE",
    }


@task
def extract_reimbursement_invoice(page: Dict[str, Any]) -> Dict[str, Any]:
    print(f"-> [Flight ticket extraction worker] Page {page['page_num']}...")
    return {
        "page_num": page["page_num"],
        "category": "REIMBURSEMENT_INVOICE",
        "employee_id": "NV-889",
        "employee_name": "Nguyen Van A",
        "route": "Hanoi - Ho Chi Minh City",
        "total_amount": 3200000,
        "is_deductible": True,
        "status": "PROCESSED_REIMBURSEMENT_MODULE",
    }


@task
def extract_invalid_invoice(page: Dict[str, Any]) -> Dict[str, Any]:
    print(f"-> [Receipt processing worker] Page {page['page_num']}...")
    return {
        "page_num": page["page_num"],
        "category": "INVALID_RECEIPT",
        "total_amount": 150000,
        "is_deductible": False,
        "alert": "NOT DEDUCTIBLE FOR CORPORATE INCOME TAX",
        "status": "FLAGGED_FOR_HUMAN_AUDIT",
    }


# Helper tasks that extract the page list for each category
@task
def get_vat_pages(groups: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    return groups.get("vat_invoices", [])

@task
def get_utility_pages(groups: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    return groups.get("utility_invoices", [])

@task
def get_reimbursement_pages(groups: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    return groups.get("reimbursement_invoices", [])

@task
def get_invalid_pages(groups: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    return groups.get("invalid_invoices", [])


@task(trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
def collect_extracted_invoices(
    vat_res: Any = None,
    utility_res: Any = None,
    reimburse_res: Any = None,
    invalid_res: Any = None,
) -> List[Dict[str, Any]]:
    """Collect all invoices once the 4 parallel extraction branches have completed safely."""
    results: List[Dict[str, Any]] = []
    for chunk in [vat_res, utility_res, reimburse_res, invalid_res]:
        if chunk is None:
            continue
        if isinstance(chunk, list):
            results.extend(chunk)
        elif isinstance(chunk, dict):
            results.append(chunk)
        else:
            try:
                for item in chunk:
                    if isinstance(item, dict):
                        results.append(item)
            except Exception:
                pass
    return results


# -------------------------------------------------------------
# 6. CHECK 2 & 3 (@task.branch - Financial Audit):
# TAX MATH & BUDGET LIMIT AUDIT (IDENTICAL TO DAGSTER)
# -------------------------------------------------------------
@task.branch
def audit_financial_budget_compliance(all_invoices: List[Dict[str, Any]]) -> str:
    """
    Verify 2 financial rules after collecting the results from the mapped loop:
    - Check 2: VAT tax formula (Total == Subtotal + VAT)
    - Check 3: Budget limit <= 100,000,000 VND and no negative amounts
    """
    total_cost = sum(inv["total_amount"] for inv in all_invoices)
    budget_limit = 100000000  # 100 million VND
    has_negative = any(inv["total_amount"] <= 0 for inv in all_invoices)

    # Verify VAT math
    vat_invoices = [inv for inv in all_invoices if inv["category"] == "VAT_INVOICE"]
    vat_math_ok = all(inv["subtotal"] + inv["vat_amount"] == inv["total_amount"] for inv in vat_invoices)

    if (total_cost <= budget_limit) and (not has_negative) and vat_math_ok:
        print(f"[FINANCIAL AUDIT PASS] Total expense {total_cost:,} VND <= Budget {budget_limit:,} VND. Ledger lock allowed.")
        return "lock_and_publish_financial_ledger"
    else:
        print(f"[FINANCIAL AUDIT FAIL] Budget violation or tax mismatch. Taking the alert branch!")
        return "alert_financial_audit_violation"


@task
def alert_financial_audit_violation():
    """Branch that handles a financial audit violation."""
    print("[ALERT] Accounting ledger locked: budget exceeded or tax amount mismatch detected!")
    return {"status": "BLOCKED_AUDIT_VIOLATION"}


@task
def lock_and_publish_financial_ledger(all_invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Branch that locks the expense ledger when all checks PASS."""
    total_expense = sum(inv["total_amount"] for inv in all_invoices)
    total_vat = sum(inv.get("vat_amount", 0) for inv in all_invoices if inv.get("is_deductible", False))

    report = {
        "pdf_source": "march_input_documents.pdf",
        "total_invoices_processed": len(all_invoices),
        "total_expense_vnd": total_expense,
        "total_vat_deductible_vnd": total_vat,
        "status": "APPROVED_AND_LOCKED_IN_ERP",
    }
    print(f"[FINANCIAL LEDGER LOCKED] Expense ledger locked: {report}")
    return report


# -------------------------------------------------------------
# DEFINING THE DAG WORKFLOW
# -------------------------------------------------------------
@dag(
    dag_id="invoice_multipage_pdf_airflow_dag",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["invoice", "multipage_pdf", "ocr", "parallel_routing", "flagship"],
    doc_md=__doc__,
)
def invoice_multipage_pdf_workflow():
    finish = EmptyOperator(
        task_id="finish",
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    # 1. Ingest PDF & Check 1 (File Integrity)
    pdf_data = ingest_multipage_invoice_pdf()
    file_branch = check_pdf_integrity(pdf_data)

    # Skip branch if the file is corrupted
    corrupted_task = handle_corrupted_pdf_file()
    file_branch >> corrupted_task >> finish

    # 2. Classify pages into 4 groups
    classified_groups = classify_invoice_pages(pdf_data)
    file_branch >> classified_groups

    # 3. Get the 4 page lists
    vat_pages = get_vat_pages(classified_groups)
    utility_pages = get_utility_pages(classified_groups)
    reimburse_pages = get_reimbursement_pages(classified_groups)
    invalid_pages = get_invalid_pages(classified_groups)

    # 4. RUN THE 4 BRANCH TASKS IN PARALLEL, CLEARLY VISIBLE IN THE GRAPH VIEW UI:
    vat_mapped = extract_vat_invoice.expand(page=vat_pages)
    utility_mapped = extract_utility_invoice.expand(page=utility_pages)
    reimburse_mapped = extract_reimbursement_invoice.expand(page=reimburse_pages)
    invalid_mapped = extract_invalid_invoice.expand(page=invalid_pages)

    # 5. Collect results from the 4 branches
    collected_invoices = collect_extracted_invoices(
        vat_res=vat_mapped,
        utility_res=utility_mapped,
        reimburse_res=reimburse_mapped,
        invalid_res=invalid_mapped,
    )

    # 6. Check 2 & 3: Financial & budget audit after collecting results
    audit_branch = audit_financial_budget_compliance(collected_invoices)

    # Violation branch
    alert_task = alert_financial_audit_violation()
    audit_branch >> alert_task >> finish

    # Success branch: lock the ledger
    success_ledger = lock_and_publish_financial_ledger(collected_invoices)
    audit_branch >> success_ledger >> finish


# Instantiate the DAG object
invoice_dag = invoice_multipage_pdf_workflow()
