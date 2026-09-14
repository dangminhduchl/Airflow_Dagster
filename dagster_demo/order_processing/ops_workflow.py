"""
Intelligent Document Processing (IDP) Workflow with Dagster (Ops & Jobs approach)
Mô phỏng 1-1 kiến trúc AWS Step Functions:
1. Task (Fetch PDF Batch)
2. Dynamic Map State (Loop fan-out từng file PDF để OCR & AI Extraction)
3. Choice State:
   - If confidence < 0.80 -> Nhánh Human Review Quarantine
   - If doc_type == 'INVOICE' -> Nhánh ERP Finance
   - If doc_type == 'CONTRACT' -> Nhánh Legal Compliance
   - If doc_type == 'ID_CARD' -> Nhánh eKYC Onboarding
4. Fan-in Aggregation (Tổng hợp kết quả toàn lô)
"""
from typing import List, Dict, Any
from dagster import op, job, DynamicOut, DynamicOutput


@op
def fetch_pdf_batch() -> List[Dict[str, Any]]:
    """Tương đương Task State: Nhận danh sách các file PDF cần xử lý."""
    return [
        {
            "doc_id": "DOC-001",
            "file_name": "hoa_don_vat_dich_vu_cloud.pdf",
            "text": "HOA DON VAT - Cty TNHH Dich Vu May - MST: 0101234567 - Tong tien: 45.000.000 VND",
        },
        {
            "doc_id": "DOC-002",
            "file_name": "hop_dong_hop_tac_techcorp.pdf",
            "text": "HOP DONG DICH VU - Doi tac: TechCorp JSC - Thoi han: 12 thang - Phat: 8%",
        },
        {
            "doc_id": "DOC-003",
            "file_name": "can_cuoc_cong_dan_nguyen_van_a.pdf",
            "text": "CAN CUOC CONG DAN - So: 001201009999 - Ho ten: NGUYEN VAN A - Nam sinh: 1995",
        },
        {
            "doc_id": "DOC-004",
            "file_name": "bien_lai_scan_mo_rach.pdf",
            "text": "??? [Corrupted scan / Blurry text] ???",
        },
    ]


@op(out=DynamicOut())
def fan_out_documents(documents: List[Dict[str, Any]]):
    """
    Tương đương Dynamic Map State (Loop fan-out):
    Tách từng file PDF thành các dynamic output để chạy song song.
    """
    for doc in documents:
        key = doc["doc_id"].replace("-", "_")
        yield DynamicOutput(value=doc, mapping_key=key)


@op
def ocr_and_ai_detect_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tương đương Task bên trong Map State:
    Mô phỏng OCR + Gọi AI Detect & phân loại Choice State đa nhánh.
    """
    doc_id = doc["doc_id"]
    file_name = doc["file_name"]

    if doc_id == "DOC-001":
        classification = "INVOICE"
        confidence = 0.96
        action = "ROUTED_TO_ERP_ORACLE"
        detail = "Hóa đơn VAT 45,000,000 VND (Cần CFO duyệt)"
    elif doc_id == "DOC-002":
        classification = "CONTRACT"
        confidence = 0.92
        action = "ROUTED_TO_LEGAL_VAULT"
        detail = "Hợp đồng TechCorp 12 tháng (Đặt lịch gia hạn)"
    elif doc_id == "DOC-003":
        classification = "ID_CARD"
        confidence = 0.98
        action = "ROUTED_TO_EKYC_CORE"
        detail = "CCCD Nguyễn Văn A - Tự động mở tài khoản"
    else:  # DOC-004
        classification = "UNREADABLE"
        confidence = 0.35
        action = "QUARANTINED_HUMAN_REVIEW"
        detail = "File mờ, độ tin cậy thấp (35%) -> Cần chuyên viên kiểm tra tay"

    print(f"[CHOICE STATE ROUTING] {doc_id} ({file_name}): Phân loại={classification} ({confidence * 100:.0f}%) -> {action} ({detail})")

    return {
        "doc_id": doc_id,
        "file_name": file_name,
        "classification": classification,
        "confidence": confidence,
        "action": action,
        "detail": detail,
        "is_quarantined": confidence < 0.80,
    }


@op
def aggregate_document_results(processed_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tương đương bước gom kết quả (Fan-in) sau khi xử lý AI xong.
    """
    auto_processed = [d for d in processed_docs if not d["is_quarantined"]]
    quarantined = [d for d in processed_docs if d["is_quarantined"]]

    summary = {
        "total_documents": len(processed_docs),
        "auto_processed_count": len(auto_processed),
        "quarantined_count": len(quarantined),
        "invoices": sum(1 for d in processed_docs if d["classification"] == "INVOICE"),
        "contracts": sum(1 for d in processed_docs if d["classification"] == "CONTRACT"),
        "ekyc": sum(1 for d in processed_docs if d["classification"] == "ID_CARD"),
        "status": "BATCH_PROCESSED_SUCCESSFULLY",
    }
    print("=" * 60)
    print(f"[BATCH REPORT] Tổng kết xử lý tài liệu OCR & AI:")
    print(f" - Tổng file: {summary['total_documents']}")
    print(f" - Tự động định tuyến thành công: {summary['auto_processed_count']}")
    print(f" - Cách ly cần kiểm tra thủ công: {summary['quarantined_count']}")
    print("=" * 60)
    return summary


@job
def document_processing_job():
    """Định nghĩa luồng Ops hoàn chỉnh cho OCR & AI Document Processing."""
    docs = fetch_pdf_batch()
    dynamic_docs = fan_out_documents(docs)
    processed = dynamic_docs.map(ocr_and_ai_detect_document)
    aggregate_document_results(processed.collect())
