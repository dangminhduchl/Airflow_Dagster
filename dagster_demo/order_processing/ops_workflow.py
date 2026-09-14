"""
Order Processing Workflow with Dagster (Ops & Jobs approach)
Mô phỏng 1-1 kiến trúc AWS Step Functions:
1. Task (Fetch Data)
2. Choice State (If-Else: Check batch validity)
3. Dynamic Map State (Loop qua từng order để xử lý song song)
4. Aggregation / Summary
"""
from typing import List, Dict, Any
from dagster import op, job, DynamicOut, DynamicOutput, Out, Output


@op(out={"orders": Out(list), "is_active": Out(bool)})
def fetch_orders_batch():
    """Tương đương Task State: Lấy danh sách các đơn hàng cần xử lý."""
    batch_data = [
        {"order_id": "ORD-001", "customer": "Alice", "amount": 1500, "item_count": 3},
        {"order_id": "ORD-002", "customer": "Bob", "amount": 250, "item_count": 1},
        {"order_id": "ORD-003", "customer": "Charlie", "amount": 3200, "item_count": 5},
        {"order_id": "ORD-004", "customer": "David", "amount": 80, "item_count": 1},
    ]
    is_active = True
    return batch_data, is_active


@op(
    out={
        "process_branch": Out(list, is_required=False),
        "skip_branch": Out(str, is_required=False),
    }
)
def check_batch_condition(orders: list, is_active: bool):
    """
    Tương đương Choice State (If-Else):
    - Nếu hệ thống active và batch có dữ liệu -> Rẽ nhánh xử lý
    - Ngược lại -> Rẽ nhánh skip / alert
    """
    if is_active and len(orders) > 0:
        print(f"[CONDITION] Batch hợp lệ với {len(orders)} đơn hàng. Rẽ nhánh xử lý.")
        yield Output(orders, output_name="process_branch")
    else:
        print("[CONDITION] Batch rỗng hoặc hệ thống bảo trì. Rẽ nhánh bỏ qua.")
        yield Output("Batch is empty or inactive", output_name="skip_branch")


@op
def log_skipped_batch(reason: str):
    """Xử lý khi nhánh If-Else đi vào trường hợp Skip."""
    print(f"[ALERT] Bỏ qua batch xử lý: {reason}")
    return {"status": "SKIPPED", "reason": reason}


@op(out=DynamicOut())
def fan_out_orders(orders: List[Dict[str, Any]]):
    """
    Tương đương Dynamic Map State (Loop fan-out):
    Tách danh sách orders thành từng dynamic output để xử lý độc lập/song song.
    """
    for order in orders:
        # mapping_key phải là chuỗi định danh duy nhất không chứa ký tự đặc biệt
        key = order["order_id"].replace("-", "_")
        yield DynamicOutput(value=order, mapping_key=key)


@op
def process_single_order(order: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tương đương Task bên trong Iterator của Map State:
    Xử lý logic cho từng đơn hàng (If-else logic giá trị đơn).
    """
    order_id = order["order_id"]
    amount = order["amount"]

    # Condition If-Else cục bộ cho từng đơn hàng
    if amount >= 1000:
        discount = amount * 0.1  # Giảm giá 10% cho đơn VIP
        tier = "VIP"
    else:
        discount = 0.0
        tier = "STANDARD"

    final_price = amount - discount
    print(f"[PROCESS] Đơn {order_id} ({tier}): Gốc={amount}$, Giảm={discount}$, Cuối={final_price}$")

    return {
        "order_id": order_id,
        "customer": order["customer"],
        "tier": tier,
        "final_price": final_price,
        "status": "COMPLETED",
    }


@op
def aggregate_results(processed_orders: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tương đương bước gom kết quả (Fan-in) sau khi Map State hoàn thành.
    """
    total_revenue = sum(item["final_price"] for item in processed_orders)
    vip_count = sum(1 for item in processed_orders if item["tier"] == "VIP")

    summary = {
        "total_orders": len(processed_orders),
        "vip_orders": vip_count,
        "total_revenue": total_revenue,
        "status": "BATCH_SUCCESS",
    }
    print(f"[SUMMARY] Tổng kết Batch: {summary}")
    return summary


@job
def order_processing_job():
    """
    Định nghĩa luồng hoàn chỉnh kết hợp:
    Fetch -> If/Else (Choice) -> Dynamic Loop (Map) -> Aggregate (Fan-in)
    """
    orders, is_active = fetch_orders_batch()
    process_branch, skip_branch = check_batch_condition(orders, is_active)

    # Nhánh Skip:
    log_skipped_batch(skip_branch)

    # Nhánh Process (Loop qua dynamic outputs):
    dynamic_orders = fan_out_orders(process_branch)
    processed = dynamic_orders.map(process_single_order)
    aggregate_results(processed.collect())
