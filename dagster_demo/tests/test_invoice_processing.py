"""
Unit tests for Multi-Page Invoice PDF Processing Pipeline in Dagster.
End-to-end tests for the Data Asset flow and all 3 validation gates (@asset_check).
"""
from dagster import materialize
from dagster_demo.invoice_processing.assets import (
    raw_multipage_invoice_pdf,
    extracted_invoice_pages,
    vat_invoices,
    utility_invoices,
    reimbursement_invoices,
    invalid_invoices,
    categorized_invoices,
    monthly_financial_expense_ledger,
    check_pdf_file_integrity,
    check_vat_tax_math,
    check_budget_limit_compliance,
)


def test_invoice_pipeline_materialization():
    """Test that the chain of 8 Assets (including the 4 parallel specialized branches) materializes successfully."""
    result = materialize(
        [
            raw_multipage_invoice_pdf,
            extracted_invoice_pages,
            vat_invoices,
            utility_invoices,
            reimbursement_invoices,
            invalid_invoices,
            categorized_invoices,
            monthly_financial_expense_ledger,
        ]
    )
    assert result.success
    assert len(result.get_asset_materialization_events()) == 8


def test_check_pdf_file_integrity():
    """Test Check 1: input PDF file integrity."""
    # 1. Valid file -> PASS
    valid_pdf = {"is_valid": True, "pages": [{"page_num": 1}], "pdf_filename": "test.pdf"}
    pass_res = check_pdf_file_integrity(valid_pdf)
    assert pass_res.passed is True

    # 2. Corrupted file / 0 pages -> FAIL
    corrupted_pdf = {"is_valid": False, "pages": [], "pdf_filename": "corrupted.pdf"}
    fail_res = check_pdf_file_integrity(corrupted_pdf)
    assert fail_res.passed is False


def test_check_vat_tax_math():
    """Test Check 2: VAT calculation correctness (Total = Subtotal + VAT)."""
    valid_data = [
        {"category": "VAT_INVOICE", "subtotal": 50000000, "vat_amount": 5000000, "total_amount": 55000000}
    ]
    pass_res = check_vat_tax_math(valid_data)
    assert pass_res.passed is True

    invalid_data = [
        {"category": "VAT_INVOICE", "page_num": 1, "subtotal": 50000000, "vat_amount": 5000000, "total_amount": 60000000}
    ]
    fail_res = check_vat_tax_math(invalid_data)
    assert fail_res.passed is False


def test_check_budget_limit_compliance_blocking():
    """Test Check 3 (BLOCKING): block if the total expense exceeds the 100 million limit."""
    valid_invoices = [
        {"total_amount": 55000000},
        {"total_amount": 1850000},
        {"total_amount": 3200000},
        {"total_amount": 150000},
    ]
    pass_res = check_budget_limit_compliance(valid_invoices)
    assert pass_res.passed is True

    overbudget_invoices = [
        {"total_amount": 120000000},
        {"total_amount": 30000000},
    ]
    fail_res = check_budget_limit_compliance(overbudget_invoices)
    assert fail_res.passed is False
    assert "BLOCKED" in fail_res.metadata["action"].value
