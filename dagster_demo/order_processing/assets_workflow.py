"""
Order Processing Workflow with Dagster (Software-Defined Assets - SDA)
Triết lý hiện đại của Dagster: Quản lý theo vòng đời dữ liệu (Data Assets)
thay vì chỉ quản lý chuỗi task thực thi.
"""
from typing import List, Dict, Any
from dagster import asset, Output, MetadataValue


@asset(group_name="orders_pipeline")
def raw_orders_batch() -> List[Dict[str, Any]]:
    """Dữ liệu đơn hàng thô lấy từ nguồn (Database/Queue/S3)."""
    return [
        {"order_id": "ORD-101", "customer": "Alice", "amount": 1200, "status": "PENDING"},
        {"order_id": "ORD-102", "customer": "Bob", "amount": 450, "status": "PENDING"},
        {"order_id": "ORD-103", "customer": "Charlie", "amount": 2500, "status": "PENDING"},
        {"order_id": "ORD-104", "customer": "Diana", "amount": 90, "status": "PENDING"},
    ]


@asset(group_name="orders_pipeline")
def validated_orders(raw_orders_batch: List[Dict[str, Any]]) -> Output[List[Dict[str, Any]]]:
    """
    Asset làm sạch và phân loại (Condition / If-Else / Logic):
    - Đơn >= 1000$: Khách VIP, chiết khấu 10%
    - Đơn < 1000$: Khách Tiêu chuẩn, không chiết khấu
    """
    cleaned = []
    for order in raw_orders_batch:
        amt = order["amount"]
        is_vip = amt >= 1000
        discount = amt * 0.10 if is_vip else 0.0
        final_price = amt - discount

        cleaned.append({
            **order,
            "tier": "VIP" if is_vip else "STANDARD",
            "discount": discount,
            "final_price": final_price,
            "status": "VALIDATED"
        })

    # Đính kèm Metadata trực quan lên Dagster Catalog UI
    metadata = {
        "total_records": len(cleaned),
        "vip_records": sum(1 for o in cleaned if o["tier"] == "VIP"),
        "preview": MetadataValue.json(cleaned[:2]),
    }
    return Output(cleaned, metadata=metadata)


@asset(group_name="orders_pipeline")
def batch_summary_report(validated_orders: List[Dict[str, Any]]) -> Output[Dict[str, Any]]:
    """
    Asset tổng hợp (Aggregate): Tính toán báo cáo tài chính của cả lô đơn hàng.
    """
    total_rev = sum(o["final_price"] for o in validated_orders)
    vip_rev = sum(o["final_price"] for o in validated_orders if o["tier"] == "VIP")
    standard_rev = sum(o["final_price"] for o in validated_orders if o["tier"] == "STANDARD")

    summary = {
        "batch_size": len(validated_orders),
        "total_revenue": total_rev,
        "vip_revenue": vip_rev,
        "standard_revenue": standard_rev,
    }

    return Output(
        summary,
        metadata={
            "total_revenue": MetadataValue.float(total_rev),
            "status": "APPROVED",
        }
    )
