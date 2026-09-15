# 🚀 Bộ Demo & So Sánh Kỹ Thuật: Apache Airflow vs. Dagster

Dự án này xây dựng **CÙNG MỘT BÀI TOÁN KINH DOANH THỰC TẾ (100% UNIFIED BUSINESS LOGIC)** trên cả hai nền tảng:
👉 **Xử lý File PDF Đa Hóa Đơn & Kiểm Định Tài Chính (Multi-Page Invoice PDF Processing & Financial Audit)**.

Mục tiêu chính: Giúp người xem nhìn thấy trực quan sự đối lập giữa **Tư duy Quản lý Task (Task-Driven của Airflow)** và **Tư duy Quản lý Tài sản Dữ liệu (Data-Driven / Asset-Driven của Dagster)** trên cùng một tập dữ liệu đầu vào và đầu ra.

---

## 📂 Cấu Trúc Thư Mục Tinh Gọn

```text
AirFlow_Dagster/
├── DOCS_Y_TUONG_VA_CAC_BUOC_DU_AN.md  # 📌 Tài liệu chi tiết: Ý tưởng, luồng 4 bước & so sánh 2 góc nhìn
├── SO_SANH_AIRFLOW_VS_DAGSTER.md      # Tài liệu so sánh chuyên sâu (DevX, Ops, Resource, Testing)
├── presentation_outline.md            # Dàn ý bài thuyết trình (12 slide + Speaker notes)
├── comparison_and_migration_guide.md  # Hướng dẫn kỹ thuật chuyển đổi từ Step Functions sang On-Prem K8s
├── README.md                          # Tài liệu tổng quan
├── run_airflow_standalone.sh          # Script khởi động nhanh Airflow UI (cổng 8080)
├── run_dagster_dev.sh                 # Script khởi động nhanh Dagster UI (cổng 3000)
│
├── airflow_demo/
│   └── dags/
│       └── invoice_multipage_pdf_dag.py   # Airflow DAG (TaskFlow API + @task.branch + .expand() loop)
│
└── dagster_demo/
    ├── definitions.py                 # Dagster unified definitions
    ├── invoice_processing/
    │   ├── __init__.py                # Module definitions
    │   └── assets.py                  # Dagster Software-Defined Assets + 3 Financial @asset_checks
    └── tests/
        └── test_invoice_processing.py # Unit tests tự động bằng pytest (Pass 100%)
```

---

## 💡 Tóm Tắt Bài Toán Xử Lý Hóa Đơn

* **File PDF đầu vào (`chung_tu_dau_vao_thang_3.pdf`)**: 4 trang gồm:
  1. *Trang 1*: Hóa đơn điện tử VAT (50tr + 5tr VAT = 55tr).
  2. *Trang 2*: Hóa đơn Tiền điện EVN (1.85tr).
  3. *Trang 3*: Hóa đơn Vé máy bay công tác phí (3.2tr).
  4. *Trang 4*: Biên lai bán lẻ không có MST (150k - cảnh báo không khấu trừ thuế).
* **3 Chốt chặn kiểm định (Checks) có mặt ở cả 2 bên**:
  - **Check 1**: Kiểm tra file PDF hợp lệ và có số trang $> 0$.
  - **Check 2**: Kiểm tra công thức thuế GTGT ($\text{Tổng} == \text{Gốc} + \text{VAT}$).
  - **Check 3**: Kiểm tra tổng chi phí $\le 100.000.000\text{ VNĐ}$ và tiền không âm.
* **Kết quả chốt sổ cái**: Tổng chi phí = **$60.200.000\text{ VNĐ}$**, VAT được khấu trừ = **$5.000.000\text{ VNĐ}$**.

---

## 🚀 Hướng Dẫn Chạy Thử Nghiệm

### 1. Khởi động Dagster UI (Cổng 3000)
```bash
./run_dagster_dev.sh
```
* **Web UI**: `http://localhost:3000`
* Xem tab **Assets** để thấy Data Lineage 4 tầng.
* Xem tab **Asset Checks** để thấy 3 chốt chặn kiểm định chất lượng.
* Bấm **Materialize all** để chạy cập nhật.

---

### 2. Khởi động Apache Airflow UI (Cổng 8080)
```bash
./run_airflow_standalone.sh
```
* **Web UI**: `http://localhost:8080`
* Bật DAG `invoice_multipage_pdf_airflow_dag` và bấm nút **Trigger DAG** (▶️).
* Xem **Graph View** để thấy luồng rẽ nhánh File Check và Dynamic Task Mapping bóc tách 4 loại hóa đơn song song.

---

### 3. Chạy Toàn Bộ Unit Test Tự Động
```bash
PYTHONPATH=. pytest dagster_demo/tests/ -v
```
*(Kết quả: 4/4 tests passed 100%).*
