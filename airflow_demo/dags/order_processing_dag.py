"""
Intelligent Document Processing (IDP) Workflow with Apache Airflow (TaskFlow API)
Mô phỏng 1-1 kiến trúc AWS Step Functions với Choice State phân luồng OCR & AI:
1. Task (Ingest PDF Batch): Nhận danh sách các file PDF
2. Dynamic Map State (.expand()): OCR & AI Detect trích xuất thông tin
3. Choice State Rẽ Nhánh Nghiệp Vụ (@task.branch):
   - Nhánh 1: Hóa đơn đỏ VAT (process_invoice_erp) -> Kế toán / ERP
   - Nhánh 2: Hợp đồng kinh tế (process_contract_legal) -> Pháp chế / Lưu trữ
   - Nhánh 3: Định danh CCCD (process_ekyc_identity) -> Mở tài khoản eKYC
   - Nhánh 4: File scan mờ (quarantine_for_human_review) -> Cách ly duyệt tay
4. Fan-in Aggregation: Báo cáo tổng hợp kết quả xử lý tự động toàn lô.
"""
from datetime import datetime
from typing import List, Dict, Any

from airflow.sdk import dag, task
from airflow.task.trigger_rule import TriggerRule
from airflow.providers.standard.operators.empty import EmptyOperator


# -------------------------------------------------------------
# 1. TASK STATE: Nhận danh sách các file PDF đầu vào
# -------------------------------------------------------------
@task
def ingest_pdf_batch() -> List[Dict[str, Any]]:
    """Tương đương Task State: Tiếp nhận lô file PDF từ S3/SFTP."""
    return [
        {
            "doc_id": "DOC-001",
            "file_name": "hoa_don_vat_dich_vu_cloud.pdf",
            "raw_text": "HOA DON VAT - Cty TNHH Dich Vu May - MST: 0101234567 - 45.000.000 VND",
            "ai_detected_type": "INVOICE",
            "confidence": 0.96,
        },
        {
            "doc_id": "DOC-002",
            "file_name": "hop_dong_hop_tac_techcorp.pdf",
            "raw_text": "HOP DONG DICH VU - Doi tac: TechCorp JSC - Thoi han: 12 thang",
            "ai_detected_type": "CONTRACT",
            "confidence": 0.92,
        },
        {
            "doc_id": "DOC-003",
            "file_name": "can_cuoc_cong_dan_nguyen_van_a.pdf",
            "raw_text": "CAN CUOC CONG DAN - So: 001201009999 - Ho ten: NGUYEN VAN A",
            "ai_detected_type": "ID_CARD",
            "confidence": 0.98,
        },
        {
            "doc_id": "DOC-004",
            "file_name": "bien_lai_scan_mo_rach.pdf",
            "raw_text": "??? [Corrupted scan / Blurry text] ???",
            "ai_detected_type": "UNREADABLE",
            "confidence": 0.35,  # Thấp < 0.80 -> Cần rẽ sang nhánh Human Review
        },
    ]


# -------------------------------------------------------------
# 2. CHOICE STATE ĐIỀU HƯỚNG THEO AI (Branching Task)
# -------------------------------------------------------------
@task.branch
def ai_routing_choice_state(doc_batch: List[Dict[str, Any]]) -> List[str]:
    """
    Choice State trong Step Functions:
    Dựa trên kết quả AI detect, trả về danh sách các nhánh nghiệp vụ cần kích hoạt.
    Các nhánh không có tài liệu tương ứng sẽ tự động bị SKIPPED trên Airflow UI!
    """
    active_routes = set()

    for doc in doc_batch:
        conf = doc.get("confidence", 0.0)
        doc_type = doc.get("ai_detected_type", "")

        if conf < 0.80:
            print(f"[CHOICE: QUARANTINE] 🚨 {doc['doc_id']} ({doc['file_name']}): Độ tin cậy thấp ({conf*100:.0f}%) -> Rẽ nhánh Human Review.")
            active_routes.add("quarantine_for_human_review")
        elif doc_type == "INVOICE":
            print(f"[CHOICE: INVOICE] 💰 {doc['doc_id']}: Hóa đơn đỏ -> Rẽ nhánh ERP Finance.")
            active_routes.add("process_invoice_erp")
        elif doc_type == "CONTRACT":
            print(f"[CHOICE: CONTRACT] ⚖️ {doc['doc_id']}: Hợp đồng kinh tế -> Rẽ nhánh Legal Vault.")
            active_routes.add("process_contract_legal")
        elif doc_type == "ID_CARD":
            print(f"[CHOICE: EKYC] 👤 {doc['doc_id']}: Căn cước công dân -> Rẽ nhánh eKYC Onboarding.")
            active_routes.add("process_ekyc_identity")

    return list(active_routes)


# -------------------------------------------------------------
# 3. CÁC NHÁNH XỬ LÝ CHUYÊN BIỆT
# -------------------------------------------------------------
@task
def process_invoice_erp(doc_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Nhánh Tài chính: Trích xuất VAT, kiểm tra hạn mức và đẩy vào Oracle/SAP ERP."""
    invoices = [d for d in doc_batch if d.get("ai_detected_type") == "INVOICE" and d.get("confidence", 0) >= 0.8]
    print(f"[ERP ACTION] Đã trích xuất {len(invoices)} hóa đơn VAT. Tổng tiền: 45,000,000 VND. Đã gửi phê duyệt chi.")
    return {"module": "FINANCE_ERP", "processed_count": len(invoices), "total_vnd": 45000000}


@task
def process_contract_legal(doc_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Nhánh Pháp lý: Lưu trữ kho dữ liệu hợp đồng và đặt lịch gia hạn tự động."""
    contracts = [d for d in doc_batch if d.get("ai_detected_type") == "CONTRACT" and d.get("confidence", 0) >= 0.8]
    print(f"[LEGAL ACTION] Đã lưu {len(contracts)} hợp đồng vào Legal Vault. Đặt lịch nhắc hạn 30 ngày trước khi hết hiệu lực.")
    return {"module": "LEGAL_COMPLIANCE", "processed_count": len(contracts)}


@task
def process_ekyc_identity(doc_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Nhánh Định danh: Tự động mở tài khoản khách hàng trên Core Banking."""
    identities = [d for d in doc_batch if d.get("ai_detected_type") == "ID_CARD" and d.get("confidence", 0) >= 0.8]
    print(f"[EKYC ACTION] Đã định danh {len(identities)} khách hàng. Tự động kích hoạt tài khoản thanh toán.")
    return {"module": "CUSTOMER_EKYC", "processed_count": len(identities)}


@task
def quarantine_for_human_review(doc_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Nhánh Cách ly: Bắn cảnh báo cho chuyên viên khi tài liệu mờ hoặc OCR không chắc chắn."""
    quarantined = [d for d in doc_batch if d.get("confidence", 0) < 0.8]
    print(f"[SECURITY ALERT] 🚨 Có {len(quarantined)} tài liệu scan mờ cần duyệt tay: {[d['file_name'] for d in quarantined]}")
    return {"module": "HUMAN_QUARANTINE", "quarantined_count": len(quarantined)}


# -------------------------------------------------------------
# 4. FAN-IN AGGREGATION: Tổng kết kết quả toàn bộ lô
# -------------------------------------------------------------
@task(trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
def aggregate_document_batch_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gom kết quả từ tất cả các nhánh đã thực thi (Fan-in).
    """
    print("=" * 60)
    print("[SUMMARY] BÁO CÁO TỔNG KẾT LÔ TÀI LIỆU OCR & AI:")
    for res in results:
        if res:
            print(f" -> Phân hệ {res.get('module')}: {res}")
    print("=" * 60)
    return {"status": "BATCH_PROCESSED_SUCCESSFULLY", "active_modules_count": len(results)}


# -------------------------------------------------------------
# DEFINING THE DAG WORKFLOW
# -------------------------------------------------------------
@dag(
    dag_id="document_processing_ai_dag",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["ocr", "ai", "idp", "step_functions", "choice_state"],
    doc_md=__doc__,
)
def document_processing_workflow():

    finish = EmptyOperator(
        task_id="finish",
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    # 1. Ingest batch
    batch_docs = ingest_pdf_batch()

    # 2. Choice State rẽ nhánh
    routing = ai_routing_choice_state(batch_docs)

    # 3. Các nhánh nghiệp vụ
    inv_res = process_invoice_erp(batch_docs)
    contract_res = process_contract_legal(batch_docs)
    ekyc_res = process_ekyc_identity(batch_docs)
    quarantine_res = quarantine_for_human_review(batch_docs)

    # Thiết lập dependency rẽ nhánh
    routing >> [inv_res, contract_res, ekyc_res, quarantine_res]

    # 4. Fan-in Aggregation
    summary = aggregate_document_batch_summary([inv_res, contract_res, ekyc_res, quarantine_res])
    summary >> finish


# Khởi tạo DAG object
doc_dag = document_processing_workflow()
