# Bộ Demo & Hướng Dẫn: Airflow vs. Dagster (Thay Thế AWS Step Functions Trên On-Premise)

Thư mục này chứa đầy đủ:
1. **Dàn ý bài thuyết trình** & **Tài liệu kỹ thuật so sánh sâu**.
2. **Mã nguồn Demo hoàn chỉnh** cho cả **Apache Airflow** và **Dagster**.
3. Các pattern cốt lõi của AWS Step Functions:
   * **Task Execution** (Tuần tự)
   * **Choice State (If-Else)** (Rẽ nhánh điều kiện)
   * **Map State (Loop song song)** (Dynamic Task Mapping / Dynamic Output)
   * **Fan-in Aggregation** (Gom kết quả sau vòng lặp)

---

## 📂 Cấu Trúc Thư Mục

```text
AirFlow_Dagster/
├── DOCS_Y_TUONG_VA_CAC_BUOC_DU_AN.md  # 📌 Tài liệu ý tưởng & giải thích luồng 4 bước chi tiết
├── SO_SANH_AIRFLOW_VS_DAGSTER.md      # Tài liệu so sánh chuyên sâu (Bảng đánh giá, Code, DevX, Ops)
├── presentation_outline.md            # Dàn ý bài thuyết trình (12 slide + Speaker notes)
├── comparison_and_migration_guide.md  # Hướng dẫn kỹ thuật chuyển đổi từ Step Functions sang On-Prem K8s
├── README.md                          # Tài liệu tổng quan
├── run_airflow_standalone.sh          # Script khởi động nhanh Airflow UI (cổng 8080)
├── run_dagster_dev.sh                 # Script khởi động nhanh Dagster UI (cổng 3000)
│
├── airflow_demo/
│   └── dags/
│       └── order_processing_dag.py    # Airflow DAG (TaskFlow API + Branching + .expand() loop)
│
└── dagster_demo/
    ├── order_processing/
    │   ├── ops_workflow.py            # Dagster Job/Ops (Mô phỏng 1-1 Step Functions)
    │   └── assets_workflow.py         # Dagster Software-Defined Assets (SDA hiện đại)
    └── tests/
        └── test_order_processing.py   # Unit test bằng pytest (Đã pass 100%)
```

---

## 🚀 Hướng Dẫn Chạy Demo

### 1. Chạy Apache Airflow (Chế độ Standalone - Không cần Docker)

Airflow đã được cài đặt sẵn. Để khởi động Airflow Web UI:

```bash
cd /home/ducdm3/Self_training/AirFlow_Dagster
./run_airflow_standalone.sh
```

* **Giao diện Web UI:** Mở trình duyệt tại `http://localhost:8080`
* Tài khoản & Mật khẩu Admin: Sẽ được in tự động trên màn hình terminal khi chạy lần đầu.
* DAG xuất hiện trên giao diện: `order_processing_airflow_dag`

---

### 2. Chạy Dagster (Dev Server) & Kiểm Thử Tự Động

#### A. Chạy Unit Test (Kiểm thử tức thì không cần bật server):
```bash
cd /home/ducdm3/Self_training/AirFlow_Dagster
PYTHONPATH=. pytest dagster_demo/tests/test_order_processing.py
```
*(Kết quả: 3/3 tests passed thành công, kiểm thử cả nhánh If-Else, Dynamic Loop và Asset Materialize).*

#### B. Mở giao diện Dagster UI:
```bash
cd /home/ducdm3/Self_training/AirFlow_Dagster
./run_dagster_dev.sh
```
* **Giao diện Web UI:** Mở trình duyệt tại `http://localhost:3000`
* Xem đồ thị Ops Workflow hoặc xem Data Lineage Catalog trực quan trong `assets_workflow.py`.

---

## 🧩 So Sánh Code Pattern Thực Tế

| Khái niệm Step Functions | Triển khai trong Airflow (`airflow_demo`) | Triển khai trong Dagster (`dagster_demo`) |
| :--- | :--- | :--- |
| **Choice State (If-Else)** | `@task.branch` trả về task_id nhánh tiếp theo | `@op` với nhiều `Out()` và `yield Output(..., output_name=...)` |
| **Map State (Loop)** | `process_single_order.expand(order=orders_list)` | `fan_out_orders` với `DynamicOut` + `.map(...)` |
| **Gom kết quả (Fan-in)** | `@task(trigger_rule="none_failed_min_one_success")` nhận list | `aggregate_results(processed.collect())` |
| **State Data Passing** | XCom tự động qua DB nội bộ | `IOManager` tự động quản lý luân chuyển dữ liệu |
