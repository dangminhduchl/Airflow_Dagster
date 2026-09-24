"""
Multi-Page Invoice PDF Processing Pipeline in Dagster (Software-Defined Assets)
100% SAME PROBLEM & SET OF CHECKS AS AIRFLOW:
- Check 1: Verify PDF file integrity (File Integrity Check)
- Check 2: Verify the VAT tax formula (Total = Subtotal + VAT)
- Check 3: Verify the expense budget limit (Total <= 100 million & Amount > 0, BLOCKING)
"""
from typing import List, Dict, Any
from dagster import (
    asset,
    asset_check,
    AssetCheckResult,
    AssetCheckSeverity,
    Output,
    MetadataValue,
)


# -------------------------------------------------------------
# ASSET 1: Raw invoice PDF file data (Raw Ingestion)
# -------------------------------------------------------------
@asset(group_name="invoice_pipeline")
def raw_multipage_invoice_pdf() -> Dict[str, Any]:
    """Data asset: combined PDF of the March input documents."""
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
# 🛡️ CHECK 1 (@asset_check: Verify PDF file integrity)
# (EQUIVALENT TO @task.branch check_pdf_integrity IN AIRFLOW)
# -------------------------------------------------------------
@asset_check(
    asset=raw_multipage_invoice_pdf,
    description="Check 1: Verify the PDF file is valid and has more than 0 pages",
)
def check_pdf_file_integrity(
    raw_multipage_invoice_pdf: Dict[str, Any]
) -> AssetCheckResult:
    """Verify the integrity of the input PDF file."""
    is_valid = raw_multipage_invoice_pdf.get("is_valid", False)
    pages = raw_multipage_invoice_pdf.get("pages", [])
    passed = is_valid and len(pages) > 0

    kwargs = {
        "passed": passed,
        "metadata": {
            "file_name": MetadataValue.text(raw_multipage_invoice_pdf.get("pdf_filename", "")),
            "total_pages": MetadataValue.int(len(pages)),
            "assessment": "FILE IS VALID AND READY FOR PROCESSING" if passed else "ERROR: FILE IS CORRUPTED OR EMPTY",
        },
    }
    if not passed:
        kwargs["severity"] = AssetCheckSeverity.ERROR

    return AssetCheckResult(**kwargs)


# -------------------------------------------------------------
# ASSET 2: Page splitting & preliminary AI extraction (Extracted Pages)
# -------------------------------------------------------------
@asset(group_name="invoice_pipeline")
def extracted_invoice_pages(
    raw_multipage_invoice_pdf: Dict[str, Any]
) -> Output[List[Dict[str, Any]]]:
    """Data asset: list of PDF pages after OCR and the AI parser."""
    pages = raw_multipage_invoice_pdf["pages"]
    extracted = []

    for p in pages:
        text = p["raw_text"].upper()
        if "VALUE-ADDED TAX" in text:
            category = "VAT_INVOICE"
        elif "ELECTRICITY" in text or "EVN" in text:
            category = "UTILITY_INVOICE"
        elif "BUSINESS TRAVEL" in text or "FLIGHT TICKET" in text:
            category = "REIMBURSEMENT_INVOICE"
        else:
            category = "INVALID_RECEIPT"

        extracted.append({
            "page_num": p["page_num"],
            "category": category,
            "raw_text": p["raw_text"],
            "ocr_confidence": 95.0 if category != "INVALID_RECEIPT" else 65.0,
            "status": "EXTRACTED",
        })

    return Output(
        extracted,
        metadata={
            "total_pages": len(extracted),
            "source_file": raw_multipage_invoice_pdf["pdf_filename"],
        },
    )


# -------------------------------------------------------------
# -------------------------------------------------------------
# 4 SPECIALIZED BRANCH ASSETS (NO IF/ELSE AT ALL)
# Shown as 4 parallel branches in the Dagster Asset Graph
# -------------------------------------------------------------
@asset(group_name="invoice_pipeline")
def vat_invoices(extracted_invoice_pages: List[Dict[str, Any]]) -> Output[List[Dict[str, Any]]]:
    """Data asset: list of extracted Value-Added Tax (VAT) invoices."""
    pages = [p for p in extracted_invoice_pages if p["category"] == "VAT_INVOICE"]
    results = [
        {
            "page_num": p["page_num"],
            "category": "VAT_INVOICE",
            "tax_code": "0101234567",
            "subtotal": 50000000,
            "vat_amount": 5000000,
            "total_amount": 55000000,
            "is_deductible": True,
        }
        for p in pages
    ]
    return Output(
        results,
        metadata={
            "count": len(results),
            "tax_code": "0101234567",
            "vat_amount_vnd": MetadataValue.int(sum(r["vat_amount"] for r in results)),
        },
    )


@asset(group_name="invoice_pipeline")
def utility_invoices(extracted_invoice_pages: List[Dict[str, Any]]) -> Output[List[Dict[str, Any]]]:
    """Data asset: list of extracted electricity / water (EVN) invoices."""
    pages = [p for p in extracted_invoice_pages if p["category"] == "UTILITY_INVOICE"]
    results = [
        {
            "page_num": p["page_num"],
            "category": "UTILITY_INVOICE",
            "customer_code": "PE0100098765",
            "service_provider": "EVN",
            "billing_period": "03/2026",
            "total_amount": 1850000,
            "is_deductible": True,
        }
        for p in pages
    ]
    return Output(
        results,
        metadata={
            "count": len(results),
            "customer_code": "PE0100098765",
            "total_utility_cost_vnd": MetadataValue.int(sum(r["total_amount"] for r in results)),
        },
    )


@asset(group_name="invoice_pipeline")
def reimbursement_invoices(extracted_invoice_pages: List[Dict[str, Any]]) -> Output[List[Dict[str, Any]]]:
    """Data asset: list of extracted travel reimbursement / flight ticket invoices."""
    pages = [p for p in extracted_invoice_pages if p["category"] == "REIMBURSEMENT_INVOICE"]
    results = [
        {
            "page_num": p["page_num"],
            "category": "REIMBURSEMENT_INVOICE",
            "employee_id": "NV-889",
            "employee_name": "Nguyen Van A",
            "route": "Hanoi - Ho Chi Minh City",
            "total_amount": 3200000,
            "is_deductible": True,
        }
        for p in pages
    ]
    return Output(
        results,
        metadata={
            "count": len(results),
            "employee_id": "NV-889",
            "total_reimbursement_vnd": MetadataValue.int(sum(r["total_amount"] for r in results)),
        },
    )


@asset(group_name="invoice_pipeline")
def invalid_invoices(extracted_invoice_pages: List[Dict[str, Any]]) -> Output[List[Dict[str, Any]]]:
    """Data asset: list of retail receipts / invalid invoices."""
    pages = [p for p in extracted_invoice_pages if p["category"] == "INVALID_RECEIPT"]
    results = [
        {
            "page_num": p["page_num"],
            "category": "INVALID_RECEIPT",
            "total_amount": 150000,
            "is_deductible": False,
            "alert": "NOT DEDUCTIBLE FOR CORPORATE INCOME TAX",
        }
        for p in pages
    ]
    return Output(
        results,
        metadata={
            "count": len(results),
            "alert": "NOT DEDUCTIBLE FOR CORPORATE INCOME TAX",
            "total_invalid_vnd": MetadataValue.int(sum(r["total_amount"] for r in results)),
        },
    )


# -------------------------------------------------------------
# RESULT COLLECTION ASSET (AUTOMATIC FAN-IN - NO IF/ELSE NEEDED)
# -------------------------------------------------------------
@asset(group_name="invoice_pipeline")
def categorized_invoices(
    vat_invoices: List[Dict[str, Any]],
    utility_invoices: List[Dict[str, Any]],
    reimbursement_invoices: List[Dict[str, Any]],
    invalid_invoices: List[Dict[str, Any]],
) -> Output[List[Dict[str, Any]]]:
    """
    Data asset: all invoices extracted from the 4 specialized branches.
    No if/else at all - Dagster automatically wires up and fans in the 4 branches here!
    """
    all_records = vat_invoices + utility_invoices + reimbursement_invoices + invalid_invoices
    total_cost = sum(r["total_amount"] for r in all_records)
    total_vat = sum(r.get("vat_amount", 0) for r in all_records)

    return Output(
        all_records,
        metadata={
            "total_invoices": len(all_records),
            "calculated_total_cost_vnd": MetadataValue.int(total_cost),
            "calculated_vat_deductible_vnd": MetadataValue.int(total_vat),
            "preview_vat_invoice": MetadataValue.json(all_records[0] if all_records else {}),
        },
    )


# -------------------------------------------------------------
# 🛡️ CHECK 2 (@asset_check: Verify the VAT tax formula)
# -------------------------------------------------------------
@asset_check(
    asset=categorized_invoices,
    description="Check 2: Verify the VAT formula (Total payment == Amount before tax + VAT)",
)
def check_vat_tax_math(
    categorized_invoices: List[Dict[str, Any]]
) -> AssetCheckResult:
    """Verify the tax calculation on VAT invoices is correct."""
    vat_invoices = [inv for inv in categorized_invoices if inv["category"] == "VAT_INVOICE"]
    math_errors = []

    for inv in vat_invoices:
        subtotal = inv.get("subtotal", 0)
        vat = inv.get("vat_amount", 0)
        total = inv.get("total_amount", 0)
        if subtotal + vat != total:
            math_errors.append(inv["page_num"])

    passed = len(math_errors) == 0
    kwargs = {
        "passed": passed,
        "metadata": {
            "vat_invoices_checked": MetadataValue.int(len(vat_invoices)),
            "math_errors_count": MetadataValue.int(len(math_errors)),
            "assessment": "TAX FORMULA 100% CORRECT" if passed else "ERROR: VAT AMOUNT MISMATCH",
        },
    }
    if not passed:
        kwargs["severity"] = AssetCheckSeverity.WARN

    return AssetCheckResult(**kwargs)


# -------------------------------------------------------------
# 🛡️ CHECK 3 (@asset_check: BLOCKING - Verify budget & negative amounts)
# -------------------------------------------------------------
@asset_check(
    asset=categorized_invoices,
    blocking=True,
    description="Check 3 (Blocking): Reject negative-amount invoices or totals over the 100 million budget cap",
)
def check_budget_limit_compliance(
    categorized_invoices: List[Dict[str, Any]]
) -> AssetCheckResult:
    """
    If the total expense in the PDF exceeds the 100,000,000 VND budget cap or any invoice is negative,
    Dagster MARKS IT FAILED and BLOCKS it from being loaded into the Expense Ledger!
    """
    total_cost = sum(inv.get("total_amount", 0) for inv in categorized_invoices)
    has_negative_amount = any(inv.get("total_amount", 0) <= 0 for inv in categorized_invoices)
    budget_limit = 100000000  # 100 million VND

    passed = (total_cost <= budget_limit) and (not has_negative_amount)

    kwargs = {
        "passed": passed,
        "metadata": {
            "total_expense_vnd": MetadataValue.int(total_cost),
            "budget_limit_vnd": MetadataValue.int(budget_limit),
            "has_negative_amount": MetadataValue.bool(has_negative_amount),
            "action": "LEDGER LOCK ALLOWED" if passed else "🚫 BLOCKED: BUDGET EXCEEDED OR NEGATIVE AMOUNT!",
        },
    }
    if not passed:
        kwargs["severity"] = AssetCheckSeverity.ERROR

    return AssetCheckResult(**kwargs)


# -------------------------------------------------------------
# ASSET 4: Corporate Expense Ledger (Downstream Ledger Asset)
# -------------------------------------------------------------
@asset(group_name="invoice_pipeline")
def monthly_financial_expense_ledger(
    categorized_invoices: List[Dict[str, Any]]
) -> Output[Dict[str, Any]]:
    """
    Final target asset: lock the monthly Expense Ledger and push it to ERP / SAP.
    Only runs when check_budget_limit_compliance (blocking=True) PASSES 100%!
    """
    total_expense = sum(inv["total_amount"] for inv in categorized_invoices)
    total_vat = sum(inv.get("vat_amount", 0) for inv in categorized_invoices if inv.get("is_deductible", False))

    ledger_summary = {
        "period": "March 2026",
        "total_invoices_recorded": len(categorized_invoices),
        "total_approved_expense_vnd": total_expense,
        "total_vat_deductible_vnd": total_vat,
        "target_erp": "SAP_Financial_Ledger",
        "status": "APPROVED_AND_LOCKED",
    }

    return Output(
        ledger_summary,
        metadata={
            "approved_expense": MetadataValue.int(total_expense),
            "vat_deductible": MetadataValue.int(total_vat),
            "compliance_status": "AUDITED_AND_COMPLIANT",
        },
    )
