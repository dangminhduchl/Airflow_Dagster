"""
Order Processing Workflow with Apache Airflow (TaskFlow API)
Mô phỏng 1-1 kiến trúc AWS Step Functions:
1. Task (Fetch Data)
2. Choice State (If-Else: Check batch condition via @task.branch)
3. Dynamic Map State (Loop song song qua từng order với Dynamic Task Mapping .expand())
4. Fan-in Aggregation (Tổng hợp kết quả sau loop với trigger_rule phù hợp)
"""
from datetime import datetime
from typing import List, Dict, Any

from airflow.sdk import dag, task
from airflow.task.trigger_rule import TriggerRule
from airflow.providers.standard.operators.empty import EmptyOperator


# -------------------------------------------------------------
# 1. TASK STATE: Fetch batch data (Module Level)
# -------------------------------------------------------------
@task
def fetch_orders_batch() -> Dict[str, Any]:
    """Tương đương Task State: Lấy danh sách các đơn hàng cần xử lý."""
    return {
        "is_active": True,
        "orders": [
            {"order_id": "ORD-001", "customer": "Alice", "amount": 1500, "item_count": 3},
            {"order_id": "ORD-002", "customer": "Bob", "amount": 250, "item_count": 1},
            {"order_id": "ORD-003", "customer": "Charlie", "amount": 3200, "item_count": 5},
            {"order_id": "ORD-004", "customer": "David", "amount": 80, "item_count": 1},
        ],
    }


# -------------------------------------------------------------
# 2. CHOICE STATE (IF - ELSE): Branching (Module Level)
# -------------------------------------------------------------
@task.branch
def check_batch_condition(batch_info: Dict[str, Any]) -> str:
    """
    Tương đương Choice State trong Step Functions:
    - If (is_active AND orders > 0) -> Nhánh 'prepare_orders_for_mapping'
    - Else -> Nhánh 'handle_skipped_batch'
    """
    is_active = batch_info.get("is_active", False)
    orders = batch_info.get("orders", [])

    if is_active and len(orders) > 0:
        print(f"[CONDITION] Batch hợp lệ ({len(orders)} orders). Tiếp tục xử lý.")
        return "prepare_orders_for_mapping"
    else:
        print("[CONDITION] Batch không hợp lệ hoặc rỗng. Rẽ sang nhánh bỏ qua.")
        return "handle_skipped_batch"


# -------------------------------------------------------------
# NHÁNH ELSE: Bỏ qua / Cảnh báo (Module Level)
# -------------------------------------------------------------
@task
def handle_skipped_batch():
    """Xử lý khi điều kiện If rẽ sang nhánh False/Skip."""
    print("[ALERT] Batch bị bỏ qua do rỗng hoặc hệ thống đang bảo trì.")
    return {"status": "SKIPPED"}


# -------------------------------------------------------------
# NHÁNH IF: Chuẩn bị danh sách cho vòng lặp Dynamic Mapping
# -------------------------------------------------------------
@task
def prepare_orders_for_mapping(batch_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    return batch_info.get("orders", [])


# -------------------------------------------------------------
# 3. DYNAMIC MAP STATE (LOOP SONG SONG): .expand() (Module Level)
# -------------------------------------------------------------
@task
def process_single_order(order: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tương đương Task bên trong Iterator của Map State:
    Xử lý từng đơn hàng độc lập, có điều kiện logic riêng (If-Else).
    """
    order_id = order["order_id"]
    amount = order["amount"]

    # Condition logic cho từng order
    if amount >= 1000:
        discount = amount * 0.10  # 10% giảm giá cho VIP
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


# -------------------------------------------------------------
# 4. AGGREGATE / FAN-IN: Thu thập kết quả sau loop (Module Level)
# -------------------------------------------------------------
@task(trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
def aggregate_results(processed_orders: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gom kết quả từ Dynamic Task Mapping (Fan-in).
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


# -------------------------------------------------------------
# DEFINING THE DAG WORKFLOW
# -------------------------------------------------------------
@dag(
    dag_id="order_processing_airflow_dag",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["migration", "step_functions", "demo"],
    doc_md=__doc__,
)
def order_processing_workflow():

    # Đánh dấu kết thúc toàn bộ DAG
    finish = EmptyOperator(
        task_id="finish",
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    # -------------------------------------------------------------
    # THIẾT LẬP GRAPH VÀ DEPENDENCY FLOW
    # -------------------------------------------------------------
    batch_data = fetch_orders_batch()
    branch_choice = check_batch_condition(batch_data)

    # Nhánh Skip
    skipped_result = handle_skipped_batch()
    branch_choice >> skipped_result >> finish

    # Nhánh Process: Dynamic Task Mapping (Loop)
    orders_list = prepare_orders_for_mapping(batch_data)
    branch_choice >> orders_list

    # .expand() chính là tính năng Map State tương tự Step Functions
    mapped_orders = process_single_order.expand(order=orders_list)
    summary_result = aggregate_results(mapped_orders)
    summary_result >> finish


# Khởi tạo DAG object
order_dag = order_processing_workflow()
