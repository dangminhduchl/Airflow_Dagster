import pytest
from dagster import materialize
from dagster_demo.order_processing.ops_workflow import (
    order_processing_job,
    process_single_order,
    fetch_orders_batch,
    check_batch_condition,
)
from dagster_demo.order_processing.assets_workflow import (
    raw_orders_batch,
    validated_orders,
    batch_summary_report,
)


def test_process_single_order_unit():
    """Test 1 op độc lập - hoàn toàn không cần cluster hay database"""
    # Test case 1: VIP order (>= 1000)
    vip_order = {"order_id": "TEST-1", "customer": "User1", "amount": 1000}
    res_vip = process_single_order(vip_order)
    assert res_vip["tier"] == "VIP"
    assert res_vip["final_price"] == 900.0  # 10% off

    # Test case 2: Standard order (< 1000)
    std_order = {"order_id": "TEST-2", "customer": "User2", "amount": 500}
    res_std = process_single_order(std_order)
    assert res_std["tier"] == "STANDARD"
    assert res_std["final_price"] == 500.0


def test_full_ops_job_execution():
    """Test toàn bộ Ops Job (Condition + Dynamic Map Loop + Fan-in)"""
    result = order_processing_job.execute_in_process()
    assert result.success
    # Kiểm tra các op đã thực thi thành công
    op_names = [event.node_name for event in result.all_node_events if event.is_step_success]
    assert "fetch_orders_batch" in op_names
    assert "check_batch_condition" in op_names
    assert "aggregate_results" in op_names


def test_assets_pipeline():
    """Test pipeline dạng Asset (SDA) bằng materialize"""
    result = materialize([raw_orders_batch, validated_orders, batch_summary_report])
    assert result.success
    
    # Kiểm tra giá trị asset sinh ra
    summary = result.output_for_node("batch_summary_report")
    assert summary["batch_size"] == 4
    assert summary["total_revenue"] > 0
