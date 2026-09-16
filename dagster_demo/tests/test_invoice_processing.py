"""
Unit tests for Multi-Page Invoice PDF Processing Pipeline in Dagster.
Kiểm thử trọn vẹn luồng Data Assets và cả 3 Chốt Chặn Kiểm Định (@asset_check).
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
    """Kiểm thử chuỗi 8 Assets (bao gồm 4 nhánh chuyên biệt song song) thành công 100%."""
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
    """Kiểm thử Check 1: Kiểm tra tính toàn vẹn file PDF đầu vào."""
    # 1. File hợp lệ -> PASS
    valid_pdf = {"is_valid": True, "pages": [{"page_num": 1}], "pdf_filename": "test.pdf"}
    pass_res = check_pdf_file_integrity(valid_pdf)
    assert pass_res.passed is True

    # 2. File bị lỗi / 0 trang -> FAIL
    corrupted_pdf = {"is_valid": False, "pages": [], "pdf_filename": "corrupted.pdf"}
    fail_res = check_pdf_file_integrity(corrupted_pdf)
    assert fail_res.passed is False


def test_check_vat_tax_math():
    """Kiểm thử Check 2: Tính chính xác của phép tính thuế VAT (Tổng = Tiền gốc + VAT)."""
    valid_data = [
        {"category": "HOA_DON_VAT", "subtotal": 50000000, "vat_amount": 5000000, "total_amount": 55000000}
    ]
    pass_res = check_vat_tax_math(valid_data)
    assert pass_res.passed is True

    invalid_data = [
        {"category": "HOA_DON_VAT", "page_num": 1, "subtotal": 50000000, "vat_amount": 5000000, "total_amount": 60000000}
    ]
    fail_res = check_vat_tax_math(invalid_data)
    assert fail_res.passed is False


def test_check_budget_limit_compliance_blocking():
    """Kiểm thử Check 3 (BLOCKING): Chặn đứng nếu tổng chi phí vượt hạn mức 100 triệu."""
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
    assert "ĐÃ CHẶN ĐỨNG" in fail_res.metadata["action"].value
