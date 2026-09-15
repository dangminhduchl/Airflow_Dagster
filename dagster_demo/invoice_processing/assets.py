"""
Multi-Page Invoice PDF Processing Pipeline in Dagster (Software-Defined Assets)
CÙNG 100% BÀI TOÁN & TẬP HỢP CÁC CHECK VỚI AIRFLOW:
- Check 1: Kiểm tra tính toàn vẹn file PDF (File Integrity Check)
- Check 2: Kiểm tra công thức tính thuế VAT (Tổng = Tiền gốc + VAT)
- Check 3: Kiểm tra hạn mức ngân sách chi phí (Tổng <= 100 triệu & Tiền > 0, BLOCKING)
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
# ASSET 1: Dữ liệu file PDF hóa đơn thô (Raw Ingestion)
# -------------------------------------------------------------
@asset(group_name="invoice_pipeline")
def raw_multipage_invoice_pdf() -> Dict[str, Any]:
    """Tài sản dữ liệu: File PDF tổng hợp chứng từ đầu vào tháng 3."""
    return {
        "pdf_filename": "chung_tu_dau_vao_thang_3.pdf",
        "is_valid": True,
        "total_pages": 4,
        "pages": [
            {
                "page_num": 1,
                "raw_text": "HÓA ĐƠN GIÁ TRỊ GIA TĂNG (VAT)\nMẫu số: 01GTKT0/001\nMã số thuế bán: 0101234567\nTiền trước thuế: 50,000,000 VND\nThuế VAT (10%): 5,000,000 VND\nTổng thanh toán: 55,000,000 VND",
            },
            {
                "page_num": 2,
                "raw_text": "HÓA ĐƠN TIỀN ĐIỆN VĂN PHÒNG (EVN)\nMã khách hàng: PE0100098765\nChỉ số cũ: 1450 - Chỉ số mới: 1890\nKỳ tiêu thụ: Tháng 03/2026\nTổng tiền thanh toán: 1,850,000 VND",
            },
            {
                "page_num": 3,
                "raw_text": "HÓA ĐƠN CÔNG TÁC PHÍ - VÉ MÁY BAY\nNhân viên: Nguyễn Văn A (Mã NV: NV-889)\nHành trình: Hà Nội - TP.HCM\nMục đích: Gặp đối tác khách hàng\nTổng tiền: 3,200,000 VND",
            },
            {
                "page_num": 4,
                "raw_text": "BIÊN LAI THU TIỀN BÁN LẺ (KHÔNG MST)\nCửa hàng tạp hóa văn phòng\nNội dung: Mua trà cà phê tiếp khách\nTổng tiền: 150,000 VND",
            },
        ],
    }


# -------------------------------------------------------------
# 🛡️ CHECK 1 (@asset_check: Kiểm tra tính toàn vẹn của File PDF)
# (TƯƠNG ĐƯƠNG @task.branch check_pdf_integrity BÊN AIRFLOW)
# -------------------------------------------------------------
@asset_check(
    asset=raw_multipage_invoice_pdf,
    description="Check 1: Kiểm tra file PDF hợp lệ và có số trang > 0",
)
def check_pdf_file_integrity(
    raw_multipage_invoice_pdf: Dict[str, Any]
) -> AssetCheckResult:
    """Kiểm tra tính toàn vẹn của tệp PDF đầu vào."""
    is_valid = raw_multipage_invoice_pdf.get("is_valid", False)
    pages = raw_multipage_invoice_pdf.get("pages", [])
    passed = is_valid and len(pages) > 0

    kwargs = {
        "passed": passed,
        "metadata": {
            "file_name": MetadataValue.text(raw_multipage_invoice_pdf.get("pdf_filename", "")),
            "total_pages": MetadataValue.int(len(pages)),
            "assessment": "FILE HỢP LỆ ĐỦ ĐIỀU KIỆN XỬ LÝ" if passed else "LỖI: FILE HỎNG HOẶC RỖNG",
        },
    }
    if not passed:
        kwargs["severity"] = AssetCheckSeverity.ERROR

    return AssetCheckResult(**kwargs)


# -------------------------------------------------------------
# ASSET 2: Tách trang & AI Bóc tách sơ bộ (Extracted Pages)
# -------------------------------------------------------------
@asset(group_name="invoice_pipeline")
def extracted_invoice_pages(
    raw_multipage_invoice_pdf: Dict[str, Any]
) -> Output[List[Dict[str, Any]]]:
    """Tài sản dữ liệu: Danh sách từng trang PDF sau khi qua OCR và AI Parser."""
    pages = raw_multipage_invoice_pdf["pages"]
    extracted = []

    for p in pages:
        text = p["raw_text"].upper()
        if "GIÁ TRỊ GIA TĂNG" in text:
            category = "HOA_DON_VAT"
        elif "TIỀN ĐIỆN" in text or "EVN" in text:
            category = "HOA_DON_TIEN_ICH"
        elif "CÔNG TÁC PHÍ" in text or "VÉ MÁY BAY" in text:
            category = "HOA_DON_CONG_TAC_PHI"
        else:
            category = "BIEN_LAI_KHONG_HOP_LE"

        extracted.append({
            "page_num": p["page_num"],
            "category": category,
            "raw_text": p["raw_text"],
            "ocr_confidence": 95.0 if category != "BIEN_LAI_KHONG_HOP_LE" else 65.0,
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
# ASSET 3: Phân loại & Cấu trúc hóa hóa đơn (Categorized Invoices)
# -------------------------------------------------------------
@asset(group_name="invoice_pipeline")
def categorized_invoices(
    extracted_invoice_pages: List[Dict[str, Any]]
) -> Output[List[Dict[str, Any]]]:
    """
    Tài sản dữ liệu: Danh sách các hóa đơn đã bóc tách chi tiết theo Schema:
    - VAT: tax_code, subtotal, vat_amount, total_amount, is_deductible
    - Tiện ích: customer_code, billing_period, total_amount
    - Công tác phí: employee_id, employee_name, total_amount
    - Biên lai: total_amount, is_deductible = False
    """
    structured_records = []
    for page in extracted_invoice_pages:
        cat = page["category"]
        p_num = page["page_num"]

        if cat == "HOA_DON_VAT":
            details = {
                "page_num": p_num,
                "category": cat,
                "tax_code": "0101234567",
                "subtotal": 50000000,
                "vat_amount": 5000000,
                "total_amount": 55000000,
                "is_deductible": True,
            }
        elif cat == "HOA_DON_TIEN_ICH":
            details = {
                "page_num": p_num,
                "category": cat,
                "customer_code": "PE0100098765",
                "service_provider": "EVN",
                "billing_period": "03/2026",
                "total_amount": 1850000,
                "is_deductible": True,
            }
        elif cat == "HOA_DON_CONG_TAC_PHI":
            details = {
                "page_num": p_num,
                "category": cat,
                "employee_id": "NV-889",
                "employee_name": "Nguyễn Văn A",
                "route": "Hà Nội - TP.HCM",
                "total_amount": 3200000,
                "is_deductible": True,
            }
        else:
            details = {
                "page_num": p_num,
                "category": cat,
                "total_amount": 150000,
                "is_deductible": False,
                "alert": "KHÔNG ĐƯỢC KHẤU TRỪ THUẾ TNDN",
            }

        structured_records.append(details)

    total_cost = sum(r["total_amount"] for r in structured_records)
    total_vat = sum(r.get("vat_amount", 0) for r in structured_records)

    return Output(
        structured_records,
        metadata={
            "total_invoices": len(structured_records),
            "calculated_total_cost_vnd": MetadataValue.int(total_cost),
            "calculated_vat_deductible_vnd": MetadataValue.int(total_vat),
            "preview_vat_invoice": MetadataValue.json(structured_records[0]),
        },
    )


# -------------------------------------------------------------
# 🛡️ CHECK 2 (@asset_check: Kiểm tra công thức tính thuế GTGT)
# -------------------------------------------------------------
@asset_check(
    asset=categorized_invoices,
    description="Check 2: Kiểm tra công thức thuế GTGT (Tổng thanh toán == Tiền trước thuế + VAT)",
)
def check_vat_tax_math(
    categorized_invoices: List[Dict[str, Any]]
) -> AssetCheckResult:
    """Kiểm tra tính chính xác của phép tính thuế trên hóa đơn VAT."""
    vat_invoices = [inv for inv in categorized_invoices if inv["category"] == "HOA_DON_VAT"]
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
            "assessment": "CÔNG THỨC THUẾ CHÍNH XÁC 100%" if passed else "LỖI: SAI LỆCH TIỀN THUẾ VAT",
        },
    }
    if not passed:
        kwargs["severity"] = AssetCheckSeverity.WARN

    return AssetCheckResult(**kwargs)


# -------------------------------------------------------------
# 🛡️ CHECK 3 (@asset_check: BLOCKING - Kiểm tra Ngân sách & Tiền âm)
# -------------------------------------------------------------
@asset_check(
    asset=categorized_invoices,
    blocking=True,
    description="Check 3: Chặn đứng (Blocking): Nghiêm cấm hóa đơn âm tiền hoặc vượt trần ngân sách 100 triệu",
)
def check_budget_limit_compliance(
    categorized_invoices: List[Dict[str, Any]]
) -> AssetCheckResult:
    """
    Nếu tổng chi phí trong file PDF vượt trần ngân sách 100.000.000 VND hoặc có hóa đơn âm,
    Dagster sẽ ĐÁNH DẤU FAILED và CHẶN ĐỨNG (BLOCK) không cho nạp vào Sổ Cái Chi Phí!
    """
    total_cost = sum(inv.get("total_amount", 0) for inv in categorized_invoices)
    has_negative_amount = any(inv.get("total_amount", 0) <= 0 for inv in categorized_invoices)
    budget_limit = 100000000  # 100 triệu VNĐ

    passed = (total_cost <= budget_limit) and (not has_negative_amount)

    kwargs = {
        "passed": passed,
        "metadata": {
            "total_expense_vnd": MetadataValue.int(total_cost),
            "budget_limit_vnd": MetadataValue.int(budget_limit),
            "has_negative_amount": MetadataValue.bool(has_negative_amount),
            "action": "CHO PHÉP CHỐT SỔ CÁI" if passed else "🚫 ĐÃ CHẶN ĐỨNG: VƯỢT NGÂN SÁCH HOẶC LỖI TIỀN ÂM!",
        },
    }
    if not passed:
        kwargs["severity"] = AssetCheckSeverity.ERROR

    return AssetCheckResult(**kwargs)


# -------------------------------------------------------------
# ASSET 4: Sổ cái Chi phí Doanh nghiệp (Downstream Ledger Asset)
# -------------------------------------------------------------
@asset(group_name="invoice_pipeline")
def monthly_financial_expense_ledger(
    categorized_invoices: List[Dict[str, Any]]
) -> Output[Dict[str, Any]]:
    """
    Asset đích cuối cùng: Chốt Sổ Cái Chi Phí Tháng và đẩy vào ERP / SAP.
    Chỉ chạy khi check_budget_limit_compliance (blocking=True) PASS 100%!
    """
    total_expense = sum(inv["total_amount"] for inv in categorized_invoices)
    total_vat = sum(inv.get("vat_amount", 0) for inv in categorized_invoices if inv.get("is_deductible", False))

    ledger_summary = {
        "period": "Tháng 03/2026",
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
