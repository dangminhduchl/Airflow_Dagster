"""
Intelligent Document Processing (IDP) Pipeline with Dagster (Software-Defined Assets)
Quy trình: Nhận PDF -> OCR & AI Detection -> Phân loại điều kiện & Kiểm định chất lượng:
1. Asset Check (@asset_check): Kiểm định độ tin cậy AI (Confidence >= 80%).
2. Đồ thị Lineage rẽ nhánh 4 bảng chuyên biệt:
   - finance_invoices_mart: Hóa đơn đỏ VAT (Tài chính / ERP)
   - legal_contracts_mart: Hợp đồng kinh tế (Pháp chế / Compliance)
   - ekyc_identities_mart: Căn cước công dân (Định danh khách hàng eKYC)
   - quarantined_unreadable_docs: Tài liệu mờ/lỗi cần nhân viên kiểm tra tay (Human-in-the-loop)
3. Fan-in Summary: Báo cáo tổng kết lô tài liệu.
"""
from typing import List, Dict, Any
from dagster import (
    asset,
    asset_check,
    Output,
    MetadataValue,
    AssetCheckResult,
    AssetCheckSeverity,
)


# ----------------------------------------------------------------------
# 1. ROOT ASSET: Lô 4 file PDF tải lên từ hệ thống cổng thông tin
# ----------------------------------------------------------------------
@asset(group_name="document_processing")
def raw_pdf_batch() -> Output[List[Dict[str, Any]]]:
    """Lô tài liệu PDF thô nhận vào từ S3 / SFTP / Portal."""
    documents = [
        {
            "doc_id": "DOC-001",
            "file_name": "hoa_don_vat_dich_vu_cloud.pdf",
            "file_size_kb": 340,
            "ocr_text_preview": "HOA DON GIA TRI GIA TANG - Cty TNHH Dich Vu May - MST: 0101234567 - Tong tien: 45.000.000 VND",
        },
        {
            "doc_id": "DOC-002",
            "file_name": "hop_dong_hop_tac_techcorp.pdf",
            "file_size_kb": 1250,
            "ocr_text_preview": "CONG HOA XA HOI CHU NGHIA VIET NAM - HOP DONG CUNG CAP DICH VU - Doi tac: TechCorp JSC - Thoi han: 12 thang",
        },
        {
            "doc_id": "DOC-003",
            "file_name": "can_cuoc_cong_dan_nguyen_van_a.pdf",
            "file_size_kb": 520,
            "ocr_text_preview": "CAN CUOC CONG DAN - So: 001201009999 - Ho va ten: NGUYEN VAN A - Nam sinh: 1995 - Quoc tich: Viet Nam",
        },
        {
            "doc_id": "DOC-004",
            "file_name": "bien_lai_scan_mo_rach.pdf",
            "file_size_kb": 95,
            "ocr_text_preview": "??? ... [Text corrupted / Low contrast scan / Unreadable characters] ... ???",
        },
    ]
    return Output(
        documents,
        metadata={
            "total_documents": len(documents),
            "preview": MetadataValue.json([d["file_name"] for d in documents]),
        },
    )


# ----------------------------------------------------------------------
# 2. OCR & AI EXTRACTION: Gọi AI trích xuất thông tin cấu trúc (Mock AI)
# ----------------------------------------------------------------------
@asset(group_name="document_processing")
def ai_extracted_documents(raw_pdf_batch: List[Dict[str, Any]]) -> Output[List[Dict[str, Any]]]:
    """Mô phỏng bước OCR + Gọi AI (LLM / Vision) phân loại và trích xuất trường dữ liệu."""
    extracted_docs = []

    for doc in raw_pdf_batch:
        doc_id = doc["doc_id"]

        if doc_id == "DOC-001":
            ai_result = {
                **doc,
                "doc_type": "INVOICE",
                "ai_confidence": 0.96,
                "structured_data": {
                    "seller": "Cty TNHH Dịch Vụ Mây",
                    "tax_id": "0101234567",
                    "amount_vnd": 45000000,
                    "vat_rate": "10%",
                },
            }
        elif doc_id == "DOC-002":
            ai_result = {
                **doc,
                "doc_type": "CONTRACT",
                "ai_confidence": 0.92,
                "structured_data": {
                    "partner": "TechCorp JSC",
                    "duration_months": 12,
                    "penalty_clause_pct": 8.0,
                    "auto_renew": True,
                },
            }
        elif doc_id == "DOC-003":
            ai_result = {
                **doc,
                "doc_type": "ID_CARD",
                "ai_confidence": 0.98,
                "structured_data": {
                    "full_name": "Nguyễn Văn A",
                    "id_number": "001201009999",
                    "birth_year": 1995,
                    "nationality": "Việt Nam",
                },
            }
        else:  # DOC-004: File mờ
            ai_result = {
                **doc,
                "doc_type": "UNKNOWN_CORRUPTED",
                "ai_confidence": 0.35,  # Thấp < 0.80
                "structured_data": {},
            }

        print(f"[AI ENGINE] {doc_id} ({doc['file_name']}): Phân loại={ai_result['doc_type']}, Độ tin cậy={ai_result['ai_confidence'] * 100:.1f}%")
        extracted_docs.append(ai_result)

    return Output(
        extracted_docs,
        metadata={
            "processed_count": len(extracted_docs),
            "ai_engine": "Mock-Vision-LLM-v2",
        },
    )


# ----------------------------------------------------------------------
# 3. ASSET CHECK: Kiểm định độ tin cậy AI (Quality Gate)
# ----------------------------------------------------------------------
@asset_check(
    asset=ai_extracted_documents,
    description="Kiểm tra chất lượng AI: Phát hiện tài liệu có độ tin cậy < 80% để cảnh báo",
)
def check_ai_confidence_quality(ai_extracted_documents: List[Dict[str, Any]]) -> AssetCheckResult:
    """Quality Gate: Cảnh báo ngay trên UI nếu có tài liệu AI không tự tin (scan mờ)."""
    low_confidence_docs = [d for d in ai_extracted_documents if d["ai_confidence"] < 0.80]
    has_low = len(low_confidence_docs) > 0

    return AssetCheckResult(
        passed=not has_low,
        severity=AssetCheckSeverity.WARN,
        metadata={
            "low_confidence_count": len(low_confidence_docs),
            "flagged_files": MetadataValue.json([d["file_name"] for d in low_confidence_docs]),
            "alert": "Phát hiện tài liệu scan mờ/lỗi OCR! Đã tự động kích hoạt cách ly kiểm tra tay."
            if has_low
            else "Tất cả tài liệu được AI nhận diện tin cậy.",
        },
    )


# ----------------------------------------------------------------------
# 4. NHÁNH 1: HÓA ĐƠN ĐỎ VAT (Finance & ERP Mart)
# ----------------------------------------------------------------------
@asset(group_name="document_processing")
def finance_invoices_mart(ai_extracted_documents: List[Dict[str, Any]]) -> Output[List[Dict[str, Any]]]:
    """Nhánh tài chính: Bảng lưu trữ hóa đơn VAT, kiểm tra duyệt chi và đẩy vào sổ kế toán ERP."""
    invoices = [
        {
            "doc_id": d["doc_id"],
            "file_name": d["file_name"],
            "seller": d["structured_data"]["seller"],
            "tax_id": d["structured_data"]["tax_id"],
            "amount_vnd": d["structured_data"]["amount_vnd"],
            "needs_cfo_approval": d["structured_data"]["amount_vnd"] >= 20000000,
            "routing": "ERP_ORACLE_FINANCE",
        }
        for d in ai_extracted_documents
        if d["doc_type"] == "INVOICE" and d["ai_confidence"] >= 0.80
    ]
    total_amount = sum(inv["amount_vnd"] for inv in invoices)

    return Output(
        invoices,
        metadata={
            "total_invoices": len(invoices),
            "total_amount_vnd": MetadataValue.float(float(total_amount)),
            "preview": MetadataValue.json(invoices),
        },
    )


# ----------------------------------------------------------------------
# 5. NHÁNH 2: HỢP ĐỒNG KINH TẾ (Legal & Compliance Mart)
# ----------------------------------------------------------------------
@asset(group_name="document_processing")
def legal_contracts_mart(ai_extracted_documents: List[Dict[str, Any]]) -> Output[List[Dict[str, Any]]]:
    """Nhánh pháp lý: Bảng hợp đồng, trích xuất điều khoản phạt và lịch gia hạn."""
    contracts = [
        {
            "doc_id": d["doc_id"],
            "file_name": d["file_name"],
            "partner": d["structured_data"]["partner"],
            "duration_months": d["structured_data"]["duration_months"],
            "penalty_rate": f"{d['structured_data']['penalty_clause_pct']}%",
            "routing": "LEGAL_VAULT_COMPLIANCE",
        }
        for d in ai_extracted_documents
        if d["doc_type"] == "CONTRACT" and d["ai_confidence"] >= 0.80
    ]
    return Output(
        contracts,
        metadata={
            "total_contracts": len(contracts),
            "preview": MetadataValue.json(contracts),
        },
    )


# ----------------------------------------------------------------------
# 6. NHÁNH 3: ĐỊNH DANH CĂN CƯỚC (eKYC Identities Mart)
# ----------------------------------------------------------------------
@asset(group_name="document_processing")
def ekyc_identities_mart(ai_extracted_documents: List[Dict[str, Any]]) -> Output[List[Dict[str, Any]]]:
    """Nhánh định danh khách hàng: Bảng dữ liệu CCCD phục vụ mở tài khoản tự động."""
    identities = [
        {
            "doc_id": d["doc_id"],
            "file_name": d["file_name"],
            "full_name": d["structured_data"]["full_name"],
            "id_number": d["structured_data"]["id_number"],
            "birth_year": d["structured_data"]["birth_year"],
            "routing": "CUSTOMER_ONBOARDING_CORE",
        }
        for d in ai_extracted_documents
        if d["doc_type"] == "ID_CARD" and d["ai_confidence"] >= 0.80
    ]
    return Output(
        identities,
        metadata={
            "total_identities": len(identities),
            "preview": MetadataValue.json(identities),
        },
    )


# ----------------------------------------------------------------------
# 7. NHÁNH 4: CÁCH LY TÀI LIỆU MỜ / LỖI (Human-In-The-Loop Quarantine)
# ----------------------------------------------------------------------
@asset(group_name="document_processing")
def quarantined_unreadable_docs(ai_extracted_documents: List[Dict[str, Any]]) -> Output[List[Dict[str, Any]]]:
    """Nhánh cách ly: Thu thập các tài liệu AI không tự tin (Confidence < 80%) để chuyên viên duyệt tay."""
    quarantined = [
        {
            "doc_id": d["doc_id"],
            "file_name": d["file_name"],
            "ai_confidence": d["ai_confidence"],
            "reason": "Low AI confidence score - Scan blurry or corrupted",
            "action_required": "MANUAL_OPERATOR_REVIEW",
        }
        for d in ai_extracted_documents
        if d["ai_confidence"] < 0.80
    ]
    return Output(
        quarantined,
        metadata={
            "quarantined_count": len(quarantined),
            "flagged_files": MetadataValue.json(quarantined),
        },
    )


# ----------------------------------------------------------------------
# 8. FAN-IN SUMMARY: Báo cáo tổng quan lô tài liệu
# ----------------------------------------------------------------------
@asset(group_name="document_processing")
def document_batch_summary(
    finance_invoices_mart: List[Dict[str, Any]],
    legal_contracts_mart: List[Dict[str, Any]],
    ekyc_identities_mart: List[Dict[str, Any]],
    quarantined_unreadable_docs: List[Dict[str, Any]],
) -> Output[Dict[str, Any]]:
    """Asset tổng hợp (Fan-in): Thống kê toàn diện kết quả xử lý lô tài liệu."""
    total_valid = len(finance_invoices_mart) + len(legal_contracts_mart) + len(ekyc_identities_mart)
    total_quarantined = len(quarantined_unreadable_docs)
    total_invoiced_vnd = sum(inv["amount_vnd"] for inv in finance_invoices_mart)

    summary = {
        "total_documents_ingested": total_valid + total_quarantined,
        "auto_processed_count": total_valid,
        "invoices_count": len(finance_invoices_mart),
        "contracts_count": len(legal_contracts_mart),
        "ekyc_count": len(ekyc_identities_mart),
        "human_review_count": total_quarantined,
        "total_invoices_amount_vnd": total_invoiced_vnd,
        "automation_success_rate": f"{(total_valid / (total_valid + total_quarantined)) * 100:.1f}%",
    }

    return Output(
        summary,
        metadata={
            "automation_rate": summary["automation_success_rate"],
            "total_invoice_vnd": MetadataValue.float(float(total_invoiced_vnd)),
            "status": "BATCH_COMPLETED",
        },
    )
