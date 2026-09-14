import pytest
from dagster import materialize
from dagster_demo.order_processing.ops_workflow import (
    document_processing_job,
    ocr_and_ai_detect_document,
    fetch_pdf_batch,
)
from dagster_demo.order_processing.assets_workflow import (
    raw_pdf_batch,
    ai_extracted_documents,
    check_ai_confidence_quality,
    finance_invoices_mart,
    legal_contracts_mart,
    ekyc_identities_mart,
    quarantined_unreadable_docs,
    document_batch_summary,
)


def test_ocr_and_ai_detect_document_unit():
    """Kiểm thử 1 Op độc lập: Đảm bảo AI phát hiện đúng loại tài liệu và cách ly file mờ"""
    # Test case 1: Hóa đơn đỏ
    inv_doc = {"doc_id": "DOC-001", "file_name": "test_invoice.pdf"}
    res_inv = ocr_and_ai_detect_document(inv_doc)
    assert res_inv["classification"] == "INVOICE"
    assert res_inv["confidence"] >= 0.90
    assert not res_inv["is_quarantined"]

    # Test case 2: File scan mờ (Low confidence) -> Cách ly
    corrupt_doc = {"doc_id": "DOC-004", "file_name": "test_blurry.pdf"}
    res_corrupt = ocr_and_ai_detect_document(corrupt_doc)
    assert res_corrupt["classification"] == "UNREADABLE"
    assert res_corrupt["confidence"] < 0.80
    assert res_corrupt["is_quarantined"]


def test_full_ops_job_execution():
    """Kiểm thử toàn bộ Ops Job mô phỏng Step Functions (Dynamic Map + Choice Routing)"""
    result = document_processing_job.execute_in_process()
    assert result.success

    summary = result.output_for_node("aggregate_document_results")
    assert summary["total_documents"] == 4
    assert summary["auto_processed_count"] == 3
    assert summary["quarantined_count"] == 1
    assert summary["invoices"] == 1
    assert summary["contracts"] == 1
    assert summary["ekyc"] == 1


def test_assets_pipeline():
    """Kiểm thử toàn bộ pipeline dạng Asset (SDA) với 4 nhánh rẽ chuyên biệt và Asset Check"""
    result = materialize(
        assets=[
            raw_pdf_batch,
            ai_extracted_documents,
            finance_invoices_mart,
            legal_contracts_mart,
            ekyc_identities_mart,
            quarantined_unreadable_docs,
            document_batch_summary,
        ],
    )
    assert result.success

    # Kiểm tra nhánh Hóa đơn
    invoices = result.output_for_node("finance_invoices_mart")
    assert len(invoices) == 1
    assert invoices[0]["amount_vnd"] == 45000000
    assert invoices[0]["needs_cfo_approval"] is True

    # Kiểm tra nhánh Hợp đồng
    contracts = result.output_for_node("legal_contracts_mart")
    assert len(contracts) == 1
    assert contracts[0]["partner"] == "TechCorp JSC"

    # Kiểm tra nhánh eKYC
    ekyc = result.output_for_node("ekyc_identities_mart")
    assert len(ekyc) == 1
    assert ekyc[0]["full_name"] == "Nguyễn Văn A"

    # Kiểm tra nhánh cách ly
    quarantined = result.output_for_node("quarantined_unreadable_docs")
    assert len(quarantined) == 1
    assert quarantined[0]["doc_id"] == "DOC-004"

    # Kiểm tra tổng hợp Fan-in
    summary = result.output_for_node("document_batch_summary")
    assert summary["auto_processed_count"] == 3
    assert summary["human_review_count"] == 1
    assert summary["total_invoices_amount_vnd"] == 45000000
