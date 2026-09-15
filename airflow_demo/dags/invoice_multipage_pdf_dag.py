"""
Multi-Page Invoice PDF Processing Workflow (Apache Airflow)
HIỂN THỊ RÕ RÀNG 4 NHÁNH RẼ SONG SONG TRÊN GRAPH VIEW UI:
1. Ingest Multi-Page PDF: Nạp file PDF tổng hợp (4 trang)
2. Check 1 (@task.branch): Kiểm tra tính toàn vẹn của File PDF
3. AI Classification & 4 Parallel Branches (.expand):
   - Nhánh 1: extract_vat_invoice (Bóc tách MST 0101234567, Tiền gốc 50tr + VAT 5tr = 55tr)
   - Nhánh 2: extract_utility_invoice (Bóc tách Mã PE0100098765, Tiền điện 1.85tr)
   - Nhánh 3: extract_reimbursement_invoice (Bóc tách Mã NV-889, Vé bay 3.2tr)
   - Nhánh 4: extract_invalid_invoice (Cảnh báo 150k không được khấu trừ thuế)
4. Check 2 & 3 (@task.branch - Financial Audit):
   - Kiểm tra công thức thuế (Tổng = Gốc + VAT)
   - Kiểm tra hạn mức ngân sách (Tổng chi phí <= 100 triệu VNĐ)
   - Nếu PASS -> Chốt Sổ Cái Kế Toán (lock_and_publish_financial_ledger)
   - Nếu VI PHẠM -> Rẽ nhánh cảnh báo kiểm toán (alert_financial_audit_violation)
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
    """Giả lập nạp 1 file PDF tổng hợp chứa nhiều trang hóa đơn (Chung 100% dữ liệu với Dagster)."""
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
# 2. CHECK 1 (@task.branch): Kiểm tra tính toàn vẹn của File
# -------------------------------------------------------------
@task.branch
def check_pdf_integrity(pdf_data: Dict[str, Any]) -> str:
    """Check cấp độ File: Hợp lệ hay Rỗng/Hỏng."""
    is_valid = pdf_data.get("is_valid", False)
    pages = pdf_data.get("pages", [])

    if is_valid and len(pages) > 0:
        print(f"[CHECK 1 PASS] File '{pdf_data.get('pdf_filename')}' hợp lệ ({len(pages)} trang). Tiếp tục bóc tách.")
        return "classify_invoice_pages"
    else:
        print("[CHECK 1 FAIL] File bị lỗi hoặc rỗng. Rẽ nhánh bỏ qua.")
        return "handle_corrupted_pdf_file"


@task
def handle_corrupted_pdf_file():
    print("[ALERT] File PDF không hợp lệ. Đã dừng quy trình xử lý.")
    return {"status": "CORRUPTED_OR_EMPTY"}


# -------------------------------------------------------------
# 3. AI PHÂN LOẠI 4 NHÓM HÓA ĐƠN
# -------------------------------------------------------------
@task
def classify_invoice_pages(pdf_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Phân loại 4 nhóm: VAT, Tiện ích, Công tác phí, Biên lai."""
    groups = {
        "vat_invoices": [],
        "utility_invoices": [],
        "reimbursement_invoices": [],
        "invalid_invoices": [],
    }

    for page in pdf_data["pages"]:
        text = page["raw_text"].upper()

        if "GIÁ TRỊ GIA TĂNG" in text or "GTKT" in text:
            groups["vat_invoices"].append({**page, "type": "HOA_DON_VAT"})
        elif "TIỀN ĐIỆN" in text or "EVN" in text or "TIỀN NƯỚC" in text:
            groups["utility_invoices"].append({**page, "type": "HOA_DON_TIEN_ICH"})
        elif "CÔNG TÁC PHÍ" in text or "VÉ MÁY BAY" in text:
            groups["reimbursement_invoices"].append({**page, "type": "HOA_DON_CONG_TAC_PHI"})
        else:
            groups["invalid_invoices"].append({**page, "type": "BIEN_LAI_KHONG_HOP_LE"})

    print(f"[AI CLASSIFIER] Phân loại thành công: VAT={len(groups['vat_invoices'])}, Tiện ích={len(groups['utility_invoices'])}, Công tác phí={len(groups['reimbursement_invoices'])}, Không hợp lệ={len(groups['invalid_invoices'])}")
    return groups


# -------------------------------------------------------------
# 4. 4 TASK RẼ NHÁNH XỬ LÝ CHUYÊN BIỆT (HIỆN RÕ TRÊN GRAPH VIEW)
# -------------------------------------------------------------
@task
def extract_vat_invoice(page: Dict[str, Any]) -> Dict[str, Any]:
    print(f"-> [Worker bóc tách VAT] Trang {page['page_num']}...")
    return {
        "page_num": page["page_num"],
        "category": "HOA_DON_VAT",
        "tax_code": "0101234567",
        "subtotal": 50000000,
        "vat_amount": 5000000,
        "total_amount": 55000000,
        "is_deductible": True,
        "status": "PROCESSED_TAX_MODULE",
    }


@task
def extract_utility_invoice(page: Dict[str, Any]) -> Dict[str, Any]:
    print(f"-> [Worker bóc tách Tiền Điện] Trang {page['page_num']}...")
    return {
        "page_num": page["page_num"],
        "category": "HOA_DON_TIEN_ICH",
        "customer_code": "PE0100098765",
        "service_provider": "EVN",
        "billing_period": "03/2026",
        "total_amount": 1850000,
        "is_deductible": True,
        "status": "PROCESSED_OPEX_MODULE",
    }


@task
def extract_reimbursement_invoice(page: Dict[str, Any]) -> Dict[str, Any]:
    print(f"-> [Worker bóc tách Vé Máy Bay] Trang {page['page_num']}...")
    return {
        "page_num": page["page_num"],
        "category": "HOA_DON_CONG_TAC_PHI",
        "employee_id": "NV-889",
        "employee_name": "Nguyễn Văn A",
        "route": "Hà Nội - TP.HCM",
        "total_amount": 3200000,
        "is_deductible": True,
        "status": "PROCESSED_REIMBURSEMENT_MODULE",
    }


@task
def extract_invalid_invoice(page: Dict[str, Any]) -> Dict[str, Any]:
    print(f"-> [Worker xử lý Biên Lai] Trang {page['page_num']}...")
    return {
        "page_num": page["page_num"],
        "category": "BIEN_LAI_KHONG_HOP_LE",
        "total_amount": 150000,
        "is_deductible": False,
        "alert": "KHÔNG ĐƯỢC KHẤU TRỪ THUẾ TNDN",
        "status": "FLAGGED_FOR_HUMAN_AUDIT",
    }


# Helper tasks trích xuất list từng loại
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
    """Gom tất cả hóa đơn sau khi 4 nhánh bóc tách song song hoàn thành an toàn."""
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
# KIỂM ĐỊNH TOÁN THUẾ & HẠN MỨC NGÂN SÁCH (ĐỒNG NHẤT VỚI DAGSTER)
# -------------------------------------------------------------
@task.branch
def audit_financial_budget_compliance(all_invoices: List[Dict[str, Any]]) -> str:
    """
    Kiểm tra 2 quy tắc tài chính sau khi gom kết quả từ vòng lặp:
    - Check 2: Công thức thuế VAT (Tổng == Gốc + VAT)
    - Check 3: Hạn mức ngân sách <= 100.000.000 VND và không có số tiền âm
    """
    total_cost = sum(inv["total_amount"] for inv in all_invoices)
    budget_limit = 100000000  # 100 triệu VNĐ
    has_negative = any(inv["total_amount"] <= 0 for inv in all_invoices)

    # Kiểm tra thuế VAT
    vat_invoices = [inv for inv in all_invoices if inv["category"] == "HOA_DON_VAT"]
    vat_math_ok = all(inv["subtotal"] + inv["vat_amount"] == inv["total_amount"] for inv in vat_invoices)

    if (total_cost <= budget_limit) and (not has_negative) and vat_math_ok:
        print(f"[FINANCIAL AUDIT PASS] Tổng chi phí {total_cost:,} VND <= Ngân sách {budget_limit:,} VND. Cho phép chốt sổ.")
        return "lock_and_publish_financial_ledger"
    else:
        print(f"[FINANCIAL AUDIT FAIL] Vi phạm ngân sách hoặc sai lệch thuế. Rẽ nhánh cảnh báo!")
        return "alert_financial_audit_violation"


@task
def alert_financial_audit_violation():
    """Nhánh xử lý khi vi phạm kiểm toán tài chính."""
    print("[ALERT] Khóa Sổ Cái Kế Toán: Phát hiện vượt hạn mức hoặc sai lệch tiền thuế!")
    return {"status": "BLOCKED_AUDIT_VIOLATION"}


@task
def lock_and_publish_financial_ledger(all_invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Nhánh chốt sổ cái chi phí thành công khi các check đều PASS."""
    total_expense = sum(inv["total_amount"] for inv in all_invoices)
    total_vat = sum(inv.get("vat_amount", 0) for inv in all_invoices if inv.get("is_deductible", False))

    report = {
        "pdf_source": "chung_tu_dau_vao_thang_3.pdf",
        "total_invoices_processed": len(all_invoices),
        "total_expense_vnd": total_expense,
        "total_vat_deductible_vnd": total_vat,
        "status": "APPROVED_AND_LOCKED_IN_ERP",
    }
    print(f"[FINANCIAL LEDGER LOCKED] Đã chốt sổ cái chi phí: {report}")
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

    # Nhánh Skip nếu file hỏng
    corrupted_task = handle_corrupted_pdf_file()
    file_branch >> corrupted_task >> finish

    # 2. Phân loại 4 nhóm trang
    classified_groups = classify_invoice_pages(pdf_data)
    file_branch >> classified_groups

    # 3. Lấy 4 list trang
    vat_pages = get_vat_pages(classified_groups)
    utility_pages = get_utility_pages(classified_groups)
    reimburse_pages = get_reimbursement_pages(classified_groups)
    invalid_pages = get_invalid_pages(classified_groups)

    # 4. CHẠY SONG SONG 4 HỘP TASK RẼ NHÁNH HIỂN THỊ RÕ RÀNG TRÊN UI GRAPH VIEW:
    vat_mapped = extract_vat_invoice.expand(page=vat_pages)
    utility_mapped = extract_utility_invoice.expand(page=utility_pages)
    reimburse_mapped = extract_reimbursement_invoice.expand(page=reimburse_pages)
    invalid_mapped = extract_invalid_invoice.expand(page=invalid_pages)

    # 5. Gom kết quả từ 4 nhánh
    collected_invoices = collect_extracted_invoices(
        vat_res=vat_mapped,
        utility_res=utility_mapped,
        reimburse_res=reimburse_mapped,
        invalid_res=invalid_mapped,
    )

    # 6. Check 2 & 3: Kiểm định tài chính & Ngân sách sau khi gom kết quả
    audit_branch = audit_financial_budget_compliance(collected_invoices)

    # Nhánh Vi phạm
    alert_task = alert_financial_audit_violation()
    audit_branch >> alert_task >> finish

    # Nhánh Thành công: Chốt sổ cái
    success_ledger = lock_and_publish_financial_ledger(collected_invoices)
    audit_branch >> success_ledger >> finish


# Khởi tạo DAG object
invoice_dag = invoice_multipage_pdf_workflow()
