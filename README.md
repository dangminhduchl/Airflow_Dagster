# Bộ Demo & Hướng Dẫn: Airflow vs. Dagster (Thay Thế AWS Step Functions Trên On-Premise)
### Bài Toán Thực Chiến: Intelligent Document Processing (OCR & AI Pipeline)

Thư mục này chứa đầy đủ:
1. **Dàn ý bài thuyết trình** & **Tài liệu kỹ thuật so sánh sâu**.
2. **Mã nguồn Demo hoàn chỉnh** cho cả **Apache Airflow** và **Dagster**.
3. Các pattern cốt lõi của AWS Step Functions trong bài toán xử lý tài liệu AI:
   * **Task Execution** (Ingest PDF thô)
   * **Dynamic Map State** (Loop bóc tách OCR song song qua từng file)
   * **Choice State (If-Else)** (AI phân loại tài liệu: Hóa đơn, Hợp đồng, eKYC hoặc Cách ly file scan mờ)
   * **Data Quality Gate** (`@asset_check` gắn huy hiệu kiểm định chất lượng AI trên UI)
   * **Fan-in Aggregation** (Gom kết quả tổng hợp tỷ lệ tự động hóa toàn lô)

---

## 📂 Cấu Trúc Thư Mục

```text
AirFlow_Dagster/
├── KICH_BAN_THUYET_TRINH_VA_DEMO.md   # 🎤 KỊCH BẢN THUYẾT TRÌNH & LIVE DEMO CHI TIẾT (Kèm lời thoại & Q&A)
├── DOCS_Y_TUONG_VA_CAC_BUOC_DU_AN.md  # 📌 Tài liệu ý tưởng & giải thích luồng OCR + AI chi tiết
├── SO_SANH_AIRFLOW_VS_DAGSTER.md      # Tài liệu so sánh chuyên sâu (Bảng đánh giá, Code, DevX, Ops)
├── presentation_outline.md            # Dàn ý bài thuyết trình (12 slide + Speaker notes)
├── comparison_and_migration_guide.md  # Hướng dẫn kỹ thuật chuyển đổi từ Step Functions sang On-Prem K8s
├── README.md                          # Tài liệu tổng quan
├── run_airflow_standalone.sh          # Script khởi động nhanh Airflow UI (cổng 8080)
├── run_dagster_dev.sh                 # Script khởi động nhanh Dagster UI (cổng 3000)
│
├── airflow_demo/
│   └── dags/
│       └── order_processing_dag.py    # Airflow DAG (document_processing_ai_dag: TaskFlow + @task.branch)
│
└── dagster_demo/
    ├── order_processing/
    │   ├── ops_workflow.py            # Dagster Job/Ops (Mô phỏng 1-1 Step Functions)
    │   └── assets_workflow.py         # Dagster Software-Defined Assets (SDA + @asset_check + Lineage)
    └── tests/
        └── test_order_processing.py   # Unit test bằng pytest (Đã pass 100%)
```

---

## 🚀 Hướng Dẫn Chạy Demo

### 1. Chạy Apache Airflow (Chế độ Standalone - Không cần Docker)

Airflow đã được cài đặt sẵn trong `.venv`. Để khởi động Airflow Web UI:

```bash
cd /home/duc/SelftTraining/Airflow_Dagster
./run_airflow_standalone.sh
```

* **Giao diện Web UI:** Mở trình duyệt tại `http://localhost:8080`
* Tài khoản & Mật khẩu Admin: Sẽ được in tự động trên màn hình terminal khi chạy lần đầu.
* DAG xuất hiện trên giao diện: `document_processing_ai_dag` (Bấm nút ▶️ để xem rẽ nhánh 4 luồng nghiệp vụ).

---

### 2. Chạy Dagster (Dev Server) & Kiểm Thử Tự Động

#### A. Chạy Unit Test (Kiểm thử tức thì không cần bật server):
```bash
cd /home/duc/SelftTraining/Airflow_Dagster
PYTHONPATH=. .venv/bin/pytest dagster_demo/tests/test_order_processing.py
```
*(Kết quả: 3/3 tests passed thành công, kiểm thử cả nhánh AI Routing, Human Review Quarantine và Asset Checks).*

#### B. Mở giao diện Dagster UI:
```bash
cd /home/duc/SelftTraining/Airflow_Dagster
./run_dagster_dev.sh
```
* **Giao diện Web UI:** Mở trình duyệt tại `http://localhost:3000`
* Xem đồ thị Ops Workflow (`document_processing_job`) hoặc xem Data Lineage rẽ nhánh 4 bảng dữ liệu chuyên biệt + huy hiệu `@asset_check` trong `assets_workflow.py`.

---

## 🧩 So Sánh Code Pattern Thực Tế

| Khái niệm Step Functions | Triển khai trong Airflow (`airflow_demo`) | Triển khai trong Dagster (`dagster_demo`) |
| :--- | :--- | :--- |
| **Choice State (If-Else)** | `@task.branch` điều hướng task theo AI detect | Phân tách Data Marts chuyên biệt (ERP, Legal, eKYC) |
| **Data Quality Gate** | Tự viết logic check trong task Python | **`@asset_check` hiển thị Badge cảnh báo trực quan trên UI** |
| **Xử lý ngoại lệ / Lỗi** | Task `quarantine_for_human_review` | Bảng `quarantined_unreadable_docs` |
| **Map State (Loop)** | Dynamic Task Mapping qua từng PDF | `fan_out_documents` với `DynamicOut` + `.map(...)` |
| **Gom kết quả (Fan-in)** | `@task(trigger_rule="none_failed_min_one_success")` | `document_batch_summary` hội tụ đa nhánh |
| **State Data Passing** | XCom tự động qua DB nội bộ | `IOManager` tự động quản lý luân chuyển dữ liệu |
