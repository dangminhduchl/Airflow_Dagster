# BỘ SLIDE THUYẾT TRÌNH: SO SÁNH THỰC CHIẾN APACHE AIRFLOW VS. DAGSTER
## Chuyên đề: Xử lý Hồ sơ Hóa đơn Đa trang & Kiểm toán Tài chính (Invoice PDF Processing)

> **Thời lượng:** 35 - 45 phút (Bao gồm Live Demo & Q&A)  
> **Người trình bày:** Tech Lead / Senior Data Engineer  
> **Khán giả:** CTO, Engineering Manager, Solution Architect, Data Platform Team  

---

## MỤC LỤC KỊCH BẢN THUYẾT TRÌNH

1. **PHẦN 1: ĐƯA RA BÀI TOÁN NGHIỆP VỤ (THE BUSINESS PROBLEM)**
   - Bối cảnh: Xử lý tệp PDF chứng từ đầu vào đa trang (`chung_tu_dau_vao_thang_3.pdf`)
   - 4 Bước quy trình & 4 Phân loại chi phí song song (VAT, Điện EVN, Công tác, Vé không hợp lệ)
   - 3 Chốt chặn kiểm định dữ liệu (Integrity, VAT Math, Ngân sách 100M VND)
   - Thách thức khi chuyển dịch từ AWS Step Functions về On-Premise/K8s

2. **PHẦN 2: LIVE DEMO HỆ THỐNG (TWO DIFFERENT WORLDS)**
   - Demo Airflow UI: Graph View, TaskFlow Branching, Dynamic Task Mapping, 4 nhánh song song
   - Demo Dagster UI: Asset Lineage Graph, Materialize in-memory, Asset Checks chặn vi phạm
   - So sánh trực quan trải nghiệm điều hành (Task-Centric vs. Asset-Centric)

3. **PHẦN 3: PHÂN TÍCH CODE AIRFLOW & CẤU TẠO HOẠT ĐỘNG NGẦM (UNDER THE HOOD)**
   - Mổ xẻ Code `invoice_multipage_pdf_dag.py`: `@dag`, `@task`, `@task.branch`, `.expand()`
   - Cấu tạo 4 trụ cột hệ thống: Scheduler, Webserver, Metadata Database, Worker/Executor
   - Vòng lặp quét DAG của Scheduler & Cơ chế luân chuyển XCom

4. **PHẦN 4: TỪ CẤU TẠO ĐẾN HẠN CHẾ CỐT TỬ $\rightarrow$ DAGSTER CÓ GÌ MỚI?**
   - Hạn chế 1: "Mù dữ liệu" (Data Blindness) $\rightarrow$ **Dagster SDA (Software-Defined Asset)**
   - Hạn chế 2: Cực hình khi viết Test & Local Debug $\rightarrow$ **Dagster Pure Functions & Pytest 0.05s**
   - Hạn chế 3: Nghẽn cổ chai XCom qua Database $\rightarrow$ **Dagster I/O Manager cắm rút**
   - Hạn chế 4: Kiến trúc Monolithic dễ sập cụm $\rightarrow$ **Dagster Daemon & gRPC Out-of-process**
   - Hạn chế 5: Thiếu Data Quality tích hợp $\rightarrow$ **Dagster `@asset_check` (blocking)**

5. **PHẦN 5: KẾT LUẬN & ĐỀ XUẤT QUYẾT ĐỊNH (TAKEAWAYS & ROADMAP)**
   - Ma trận chấm điểm kỹ thuật có trọng số
   - Định vị ứng dụng: Ai phù hợp cho cái gì?
   - Lộ trình di chuyển 3 giai đoạn lên On-Premise / K8s
   - Q&A & Kế hoạch hành động

---

<!-- ========================================================================= -->
<!-- PHẦN 1: ĐƯA RA BÀI TOÁN -->
<!-- ========================================================================= -->

# PHẦN 1: ĐƯA RA BÀI TOÁN NGHIỆP VỤ

---

## SLIDE 1: TRANG TIÊU ĐỀ
### **SO SÁNH THỰC CHIẾN AIRFLOW VS. DAGSTER**
#### *Từ Cấu Tạo Cốt Lõi, Điểm Nghẽn Kỹ Thuật Đến Trải Nghiệm Xử Lý Dữ Liệu Hiện Đại*

* **Diễn giả:** [Họ và Tên] - Solution Architect / Data Platform Lead
* **Bối cảnh:** Dự án chuyển dịch luồng xử lý tự động từ AWS Step Functions về cụm On-Premise / Kubernetes.

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Kính chào anh chị và ban lãnh đạo. Khi đưa các quy trình xử lý dữ liệu và AI từ Cloud về hạ tầng On-Premise, câu hỏi lớn nhất luôn là: 'Chúng ta nên dùng công cụ nào để điều phối?'. 
> Hôm nay, chúng ta không so sánh lý thuyết chung chung. Chúng ta sẽ lấy một bài toán nghiệp vụ thật 100%: Xử lý tập hóa đơn đa trang và kiểm toán chi phí tài chính, sau đó phân tích sâu từ cấu tạo ngầm, code thực tế, đến lý do vì sao kiến trúc cũ lại gặp điểm nghẽn và giải pháp thế hệ mới giải quyết ra sao."

---

## SLIDE 2: BÀI TOÁN THỰC TẾ: XỬ LÝ HÓA ĐƠN PDF ĐA TRANG
### **Tệp PDF đầu vào: `chung_tu_dau_vao_thang_3.pdf` (4 trang chứng từ hỗn hợp)**

* **Thực tế doanh nghiệp**: Hóa đơn đầu vào quét về không nằm ở từng file riêng lẻ mà gom thành 1 file PDF scan tổng hợp gồm nhiều trang, thuộc nhiều loại chi phí khác nhau.
* **Cơ cấu 4 trang trong file mẫu**:
  * **Trang 1**: Hóa đơn GTGT dịch vụ Cloud Server (FPT Telecom) - 15.000.000 VNĐ (VAT 10% = 1.500.000 VNĐ).
  * **Trang 2**: Hóa đơn tiền điện văn phòng (EVN Hà Nội) - 8.500.000 VNĐ (VAT 8% = 680.000 VNĐ).
  * **Trang 3**: Giấy đề nghị thanh toán công tác phí của nhân viên - 4.200.000 VNĐ (Không thuế VAT).
  * **Trang 4**: Biên lai vé cầu đường cũ mờ (Không hợp lệ, thiếu MST và chữ ký số).

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Mỗi đầu tháng, phòng kế toán nhận hàng trăm file PDF scan. Điển hình như file `chung_tu_dau_vao_thang_3.pdf` này. File gồm 4 trang nhưng tính chất khác nhau hoàn toàn: có hóa đơn VAT chuẩn, có hóa đơn điện EVN, có thanh toán công tác phí không thuế, và có cả chứng từ rác không hợp lệ. Hệ thống bắt buộc phải tự động bóc tách, rẽ đúng nhánh xử lý, kiểm tra toán học và chặn đứng các sai phạm ngân sách."

---

## SLIDE 3: QUY TRÌNH 4 BƯỚC & 3 CHỐT CHẶN KIỂM ĐỊNH
### **Luồng Nghiệp Vụ Song Song & Kiểm Toán Ngân Sách**

```text
[PDF Hóa Đơn 4 Trang]
       │
       ▼ (Check 1: File Integrity - File hợp lệ > 0 trang)
[Tách Từng Trang (Page Splitter)]
       │
       ├─────────────────┬──────────────────┬─────────────────┐
       ▼                 ▼                  ▼                 ▼
[Nhánh 1: VAT]   [Nhánh 2: EVN]     [Nhánh 3: Công tác] [Nhánh 4: Invalid]
 (FPT Server)     (Điện văn phòng)   (Thanh toán tạm)     (Biên lai hỏng)
       │                 │                  │                 │
       └─────────────────┴──────────────────┴─────────────────┘
                                 │
                                 ▼ (Check 2: VAT Tax Math: Total == Subtotal + VAT)
                                 ▼ (Check 3: Budget Limit <= 100.000.000 VNĐ)
                  [Ghi Sổ Cái Kế Toán (Expense Ledger)]
```

* **Chốt chặn 1 (File Integrity)**: Kiểm tra file PDF có bị hỏng (corrupt) không, số trang > 0.
* **Chốt chặn 2 (VAT Tax Math)**: Xác thực công thức thuế: `Total = Subtotal + VAT`.
* **Chốt chặn 3 (Budget Compliance)**: Chặn đứng mọi hóa đơn có tổng tiền > 100.000.000 VNĐ hoặc $\le$ 0. Nếu vi phạm, **tuyệt đối không cho phép ghi vào sổ cái**!

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Đây là luồng nghiệp vụ 100% giống nhau mà chúng ta sẽ yêu cầu cả Airflow và Dagster cùng giải quyết. Nhìn sơ đồ rất đơn giản, nhưng để thể hiện được 4 nhánh rẽ song song trên giao diện, và đặc biệt là cơ chế 'chặn đứng khi vi phạm ngân sách', hai hệ thống sẽ giải quyết theo hai trường phái kiến trúc đối lập nhau hoàn toàn."

---

<!-- ========================================================================= -->
<!-- PHẦN 2: DEMO HỆ THỐNG -->
<!-- ========================================================================= -->

# PHẦN 2: LIVE DEMO HỆ THỐNG (TWO WORLDS)

---

## SLIDE 4: DEMO TRÊN AIRFLOW UI
### **TaskFlow API, Dynamic Branching & Dynamic Task Mapping**

* **Giao diện Graph View**:
  * Hiển thị nhánh rẽ từ `branch_by_invoice_type`: rẽ vào 4 hàm `@task` chuyên biệt.
  * Sử dụng cơ chế `.expand()`: các trang cùng loại chạy song song dưới dạng mapped instances.
  * Dùng `TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS` để gộp 4 nhánh về `aggregate_monthly_ledger`.
* **Cơ chế chặn vi phạm**:
  * Dùng task rẽ nhánh `branch_on_budget_compliance` $\rightarrow$ Nhảy sang task `flag_budget_violation` và bỏ qua (`skip`) task `commit_to_database`.

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Xin mời các anh chị quan sát màn hình Airflow tại cổng 8080. 
> Trên Graph View, Airflow vẽ đồ thị các ô vuông biểu thị cho các 'Task' (Hành động). Khi kích hoạt DAG, ta thấy nhánh rẽ xuất hiện. Các trang được đẩy vào từng hộp xử lý. 
> Tuy nhiên, hãy để ý: Airflow chỉ báo trạng thái Xanh lá cây (Success) hoặc Đỏ (Failed). Bản thân giao diện Airflow không cho ta biết bên trong mỗi hộp đó dữ liệu gồm những hóa đơn nào, trị giá bao nhiêu tiền, trừ khi ta phải bấm vào từng task rồi mò vào tab XCom hoặc đọc hàng trăm dòng log chữ đen."

---

## SLIDE 5: DEMO TRÊN DAGSTER UI
### **Software-Defined Assets & Asset Checks Trực Quan Hóa**

* **Giao diện Asset Lineage (Phả hệ Dữ liệu)**:
  * Không vẽ task vô định, mà vẽ **Tài sản dữ liệu (Data Assets)**:
    `raw_multipage_invoice_pdf` $\rightarrow$ `extracted_invoice_pages` $\rightarrow$ `categorized_invoices` $\rightarrow$ `monthly_financial_expense_ledger`.
* **Chốt chặn Asset Checks hiển thị cấp 1 (First-Class Citizen)**:
  * Đi kèm mỗi Asset là các tag Check màu xanh/đỏ: `check_pdf_file_integrity`, `check_vat_tax_math`, `check_budget_limit_compliance`.
  * Khi ngân sách vượt 100M VND $\rightarrow$ Check văng `PASSED: False` với thuộc tính `blocking=True`, **lập tức ngắt luồng**, Asset sổ cái hạ nguồn không được sinh ra!

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Bây giờ, hãy nhìn sang giao diện Dagster tại cổng 3000. 
> Đây là điều khác biệt lớn nhất: Thay vì nhìn thấy các tác vụ vô hình, ta nhìn thấy chính xác 'Hóa đơn tháng 3' và 'Sổ cái kế toán'. 
> Đặc biệt, nhìn vào ô `monthly_financial_expense_ledger`, có 2 chiếc khiên bảo vệ màu xanh: đó là Asset Checks. Nếu kế toán nạp nhầm hóa đơn 120 triệu, chiếc khiên chuyển sang màu đỏ rực, pipeline dừng lại ngay lập tức và ghi rõ lý do vi phạm metadata ngay trên màn hình chính mà không cần lục log."

---

<!-- ========================================================================= -->
<!-- PHẦN 3: PHÂN TÍCH CODE AIRFLOW & CẤU TẠO HOẠT ĐỘNG NGẦM -->
<!-- ========================================================================= -->

# PHẦN 3: PHÂN TÍCH CODE AIRFLOW & CẤU TẠO HOẠT ĐỘNG NGẦM

---

## SLIDE 6: MỔ XẺ FILE CODE AIRFLOW (`invoice_multipage_pdf_dag.py`)
### **Cách Định Nghĩa Task, Branching và Luân Chuyển Dữ Liệu**

```python
# 1. ĐỊNH NGHĨA DAG & TASK CƠ BẢN
@dag(dag_id="invoice_multipage_pdf_dag", schedule=None)
def invoice_multipage_pdf_dag():
    
    # 2. TASK RẼ NHÁNH: Trả về string là task_id tiếp theo
    @task.branch
    def check_file_integrity_and_branch(file_meta: dict):
        if file_meta.get("is_valid") and file_meta.get("total_pages", 0) > 0:
            return "extract_pages"
        return "quarantine_corrupt_pdf"

    # 3. DYNAMIC MAPPING: Xử lý song song theo danh sách trang
    @task
    def extract_vat_invoice(page: dict) -> dict: ...
    @task
    def extract_utility_invoice(page: dict) -> dict: ...

    vat_results = extract_vat_invoice.expand(page=vat_pages)

    # 4. GỘP CÁC NHÁNH BỎ QUA (SKIPPED): Phải dùng TriggerRule đặc biệt
    @task(trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
    def aggregate_monthly_ledger(all_processed_pages: list): ...
```

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Hãy mổ xẻ code Airflow mà chúng ta vừa viết:
> Thứ nhất: `@task.branch` bắt buộc hàm phải trả về string chứa tên của `task_id` tiếp theo. Nghĩa là code logic nghiệp vụ bị trói cứng vào tên của task trong DAG.
> Thứ hai: Để 4 nhánh chạy song song nhưng không bị lỗi khi một vài nhánh không có trang nào, ta phải cấu hình `TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS`. Nếu quên dòng này, toàn bộ pipeline sẽ bị treo hoặc báo fail do cơ chế mặc định `all_success`.
> Thứ ba: Làm sao dữ liệu đi từ hàm này sang hàm kia? Đó là qua cơ chế XCom."

---

## SLIDE 7: CẤU TẠO 4 THÀNH PHẦN TRỤ CỘT CỦA AIRFLOW
### **Kiến Trúc Được Thiết Kế Từ Năm 2014 (Airbnb)**

```text
┌─────────────────────────────────────────────────────────────┐
│                      APACHE AIRFLOW                         │
│                                                             │
│   ┌───────────────┐     Quét code liên tục   ┌───────────┐  │
│   │   Webserver   │ ◄──────────────────────► │ Scheduler │  │
│   └───────┬───────┘                          └─────┬─────┘  │
│           │                                        │        │
│           │ Đọc/Ghi trạng thái task, XCom, logs    │        │
│           ▼                                        ▼        │
│     ┌─────────────────────────────────────────────────┐     │
│     │        Metadata Database (PostgreSQL)           │     │
│     └─────────────────────────────────────────────────┘     │
│                              ▲                              │
│                              │ Ghi nhận trạng thái hoàn tất │
│                   ┌──────────┴──────────┐                   │
│                   │   Worker/Executor   │                   │
│                   │ (Celery / K8s Pods) │                   │
│                   └─────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

* **Scheduler (Bộ não)**: Chạy vòng lặp (Heartbeat loop) vô tận, liên tục nạp file Python từ ổ đĩa để tính toán đồ thị phụ thuộc.
* **Metadata Database (Trái tim)**: Chứa toàn bộ trạng thái DAG Run, Task Instance, User, Connection và dữ liệu XCom.
* **Executor / Worker**: Nhận lệnh từ Scheduler để chạy các tiến trình Python con.

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Để hiểu vì sao Airflow gặp khó khăn với các bài toán dữ liệu hiện đại, ta phải nhìn vào cấu tạo 4 thành phần này. 
> Airflow ra đời năm 2014, thời điểm mà người ta chỉ cần một công cụ Cronjob mạnh mẽ để kích hoạt các job Hadoop/Hive chạy ban đêm. 
> Mọi giao tiếp giữa Scheduler, Webserver và Worker đều đi qua một chiếc 'nút cổ chai' duy nhất: Metadata Database PostgreSQL."

---

## SLIDE 8: CÁCH CHẠY NGẦM CỐT LÕI CỦA AIRFLOW
### **Vòng Lặp Phân Tích (DAG Parsing Loop) & XCom Lifecycle**

* **1. Chu kỳ quét file (DAG Parsing)**:
  * Scheduler không lưu code cố định trên RAM. Cứ mỗi $N$ giây (mặc định 30s), nó đọc lại toàn bộ code của mọi file trong thư mục `dags/`.
  * Nếu trong file có code gọi API bên ngoài hoặc import thư viện nặng $\rightarrow$ Scheduler bị nghẽn (CPU Spike).
* **2. Vòng đời thực thi Task**:
  `NONE` $\rightarrow$ `SCHEDULED` $\rightarrow$ `QUEUED` $\rightarrow$ `RUNNING` $\rightarrow$ `SUCCESS` / `FAILED`
* **3. Cơ chế XCom (Cross-Communication)**:
  * Khi hàm `extract_pages` trả về 1 danh sách dict: Airflow serialize đối tượng thành chuỗi JSON / Pickle rồi chèn (INSERT) vào bảng `xcom` trong Database PostgreSQL!
  * Task tiếp theo đọc dữ liệu bằng cách thực hiện câu lệnh `SELECT ... FROM xcom`.

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Khi một task return về dữ liệu trong Airflow, dữ liệu đó bị biến thành chuỗi text và ném thẳng vào database PostgreSQL của hệ thống. Nếu danh sách hóa đơn lớn hoặc chứa file ảnh base64, database của Airflow sẽ nhanh chóng bị phình to (bloat), làm chậm toàn bộ cụm điều phối!"

---

<!-- ========================================================================= -->
<!-- PHẦN 4: TỪ CẤU TẠO ĐẾN HẠN CHẾ CỐT TỬ -> DAGSTER CÓ GÌ MỚI -->
<!-- ========================================================================= -->

# PHẦN 4: TỪ CẤU TẠO $\rightarrow$ HẠN CHẾ CỐT TỬ $\rightarrow$ DAGSTER GIẢI QUYẾT RA SAO?

---

## SLIDE 9: HẠN CHẾ 1: "MÙ DỮ LIỆU" (DATA BLINDNESS)
### **Nỗi Đau: Task Thành Công Nhưng Dữ Liệu Hỏng**

* **Gốc rễ cấu tạo của Airflow**: 
  * Airflow là **Task-Centric**. Nó chỉ quan tâm tiến trình chạy có trả về mã thoát `0` hay không.
  * Task bóc tách hóa đơn xong trả về file rỗng $\rightarrow$ Airflow vẫn bật đèn xanh `SUCCESS`.
* **Dagster giải quyết bằng: Software-Defined Assets (SDA)**:
  * Đổi tư duy từ: *"Tôi phải chạy hàm gì?"* sang *"Tôi đang tạo ra tài sản dữ liệu gì?"*.
  * Asset phản ánh trạng thái thực của dữ liệu: phiên bản dữ liệu (data version), schema, số lượng dòng, thời điểm cập nhật cuối cùng.

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Điểm hạn chế đầu tiên sinh ra từ cấu tạo Task-centric: Airflow hoàn toàn 'mù' về dữ liệu. Với kế toán, họ không cần biết bạn chạy bao nhiêu Task, họ chỉ cần biết: 'Hóa đơn tháng 3 đã sẵn sàng chưa và số liệu có chuẩn không?'. Dagster đưa Dữ liệu trở thành công dân hạng nhất, phản ánh trung thực giá trị nghiệp vụ."

---

## SLIDE 10: HẠN CHẾ 2: CỰC HÌNH VIẾT TEST & LOCAL DEBUG
### **Nỗi Đau: Muốn Test 1 Hàm Phải Dựng Cả Cụm Database**

* **Gốc rễ cấu tạo của Airflow**:
  * Các task của Airflow bị trói chặt vào `Airflow Context` (`ti`, `run_id`, `xcom_pull`, DB Connection).
  * Viết `pytest` cho 1 task bình thường sẽ văng lỗi `KeyError: 'ti'` ngay lập tức.
  * Muốn Integration Test toàn bộ DAG, bắt buộc phải khởi tạo Database PostgreSQL/SQLite, chạy `airflow db migrate` rất nặng và chậm trong CI/CD.
* **Dagster giải quyết bằng: Pure Python Function & `materialize()` in RAM**:
  * Asset bản chất là một **hàm Python thuần khiết**.
  * Chạy test bằng `pytest` xong trong **0.05 giây**:

```python
# Test trọn vẹn pipeline trong RAM, KHÔNG CẦN DATABASE, KHÔNG CẦN SERVER:
def test_invoice_pipeline():
    result = materialize([
        raw_multipage_invoice_pdf, 
        extracted_invoice_pages, 
        categorized_invoices
    ])
    assert result.success
```

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Đây chính là câu trả lời vì sao Dagster lại dễ test hơn Airflow gấp 10 lần. 
> Trong file `test_invoice_processing.py`, chúng ta vừa chạy 4 bài test chỉ trong 0.12 giây bằng Pytest. Không cần mở Webserver, không cần Postgres, không sinh ra một file rác nào trên ổ cứng. Lập trình viên có thể viết test TDD ngay trên máy cá nhân trước khi đẩy code lên Git."

---

## SLIDE 11: HẠN CHẾ 3: NGHẼN CỔ CHAI XCOM
### **Nỗi Đau: Dữ Liệu Bị Ép Đi Qua Database Hệ Thống**

* **Gốc rễ cấu tạo của Airflow**:
  * XCom lưu vào Metadata DB $\rightarrow$ Giới hạn kích thước vài megabyte. Muốn lưu file to, developer phải tự viết code upload lên MinIO/S3, rồi truyền đường dẫn string qua XCom $\rightarrow$ Code bị bẩn bởi logic hạ tầng.
* **Dagster giải quyết bằng: I/O Manager (Cắm - Rút Lưu Trữ)**:
  * Tách biệt 100% giữa **Logic tính toán** và **Nơi lưu trữ**:
    * Môi trường **Production**: I/O Manager tự động đẩy kết quả lên S3/MinIO bucket.
    * Môi trường **Local / CI Test**: I/O Manager tự động giữ trong bộ nhớ RAM (`mem_io_manager`).
  * Code của lập trình viên hoàn toàn sạch sẽ, không chứa một dòng code S3 hay path ổ đĩa nào!

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "I/O Manager của Dagster là một cuộc cách mạng về thiết kế phần mềm (Dependency Injection). Lập trình viên chỉ cần `return df` hoặc `return invoice_dict`. Việc lưu nó vào MinIO, S3 hay Postgres là do I/O Manager đảm nhận bên ngoài. Khi test, ta rút S3 ra và cắm RAM vào, cực kỳ linh hoạt."

---

## SLIDE 12: HẠN CHẾ 4: MONOLITHIC PARSING & RỦI RO SẬP CỤM
### **Nỗi Đau: Một File DAG Lỗi Cú Pháp Làm Treo Toàn Cụm Scheduler**

* **Gốc rễ cấu tạo của Airflow**:
  * Scheduler nạp trực tiếp file code Python của người dùng vào cùng một tiến trình hệ điều hành.
  * Nếu ai đó viết lệnh cài sai thư viện hoặc vòng lặp vô tận trong file DAG, Scheduler có thể bị sập hoàn toàn.
* **Dagster giải quyết bằng: Kiến Trúc gRPC Out-Of-Process**:
  * Webserver và Daemon chạy tách biệt 100% với Code người dùng qua cổng kết nối gRPC.
  * Code xử lý hóa đơn chạy trong Container riêng (Code Location). Nếu code có bị crash bộ nhớ (OOM), giao diện Dagster vẫn sáng đèn hoạt động bình thường và báo lỗi cách ly chính xác tại dòng đó!

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Về mặt DevOps và bảo mật hệ thống, kiến trúc tách rời của Dagster ăn đứt Airflow. Trên Kubernetes, mỗi team có thể deploy một Code Location Pod riêng với thư viện Python độc lập. Team Hóa đơn dùng Python 3.12 không sợ bị xung đột thư viện với Team Machine Learning dùng Python 3.9."

---

## SLIDE 13: HẠN CHẾ 5: THIẾU KIỂM ĐỊNH CHẤT LƯỢNG DỮ LIỆU
### **Nỗi Đau: Dữ Liệu Bẩn Vẫn Lọt Vào Database Kế Toán**

* **Gốc rễ cấu tạo của Airflow**:
  * Muốn kiểm tra dữ liệu, phải tự đẻ thêm hàng tá task phụ: `validate_task`, `check_task`, `branch_task` làm đồ thị DAG phình to rối rắm.
* **Dagster giải quyết bằng: First-Class Asset Checks**:
  * Gắn trực tiếp kiểm định vào Asset:
```python
@asset_check(asset=monthly_financial_expense_ledger, blocking=True)
def check_budget_limit_compliance(monthly_financial_expense_ledger: dict):
    total = monthly_financial_expense_ledger.get("grand_total", 0)
    passed = (0 < total <= 100_000_000)
    return AssetCheckResult(
        passed=passed, 
        metadata={"total_amount": total, "threshold": 100_000_000}
    )
```
  * Thuộc tính `blocking=True`: Tự động ngắt luồng ngay lập tức khi phát hiện gian lận/sai lệch dữ liệu!

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Với Airflow, muốn kiểm định dữ liệu ta phải viết các hàm rẽ nhánh phức tạp. Với Dagster, `@asset_check` là công dân hạng nhất. Nó vừa kiểm tra, vừa ghi nhận điểm số chất lượng (Data Observability), vừa có quyền lực tối cao để chặn đứng pipeline khi có rủi ro tài chính."

---

<!-- ========================================================================= -->
<!-- PHẦN 5: KẾT LUẬN & ĐỀ XUẤT -->
<!-- ========================================================================= -->

# PHẦN 5: KẾT LUẬN & ĐỀ XUẤT QUYẾT ĐỊNH

---

## SLIDE 14: MA TRẬN SO SÁNH TỔNG HỢP 7 TIÊU CHÍ

| Tiêu Chí Kỹ Thuật | Apache Airflow 2.x | Dagster | Người Thắng Cuộc |
| :--- | :--- | :--- | :---: |
| **1. Triết lý vận hành** | Task-Centric (Chạy tác vụ) | Asset-Centric (Quản lý dữ liệu) | **Dagster** |
| **2. Tốc độ & Khả năng Test** | Khó khăn, phụ thuộc Database | Dễ dàng, chạy `pytest` trong RAM | **Dagster (Vượt trội)** |
| **3. Luân chuyển dữ liệu** | XCom nghẽn qua DB | I/O Manager tách rời lưu trữ | **Dagster** |
| **4. Kiểm soát chất lượng** | Phải tự code thủ công | Asset Checks tích hợp sẵn (`blocking`) | **Dagster** |
| **5. Cô lập môi trường (K8s)** | Khá nặng, chung scheduler | Giao thức gRPC phân tán | **Dagster** |
| **6. Hệ sinh thái & Cộng đồng** | Khổng lồ (ra mắt 2014) | Trẻ hơn nhưng phát triển bùng nổ | **Airflow** |
| **7. Đổi mới & Trải nghiệm Dev** | Chậm chạp, mang gánh nặng di sản | Hiện đại, chuẩn Software Engineering | **Dagster** |

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Nhìn vào bảng tổng kết 7 tiêu chí: Airflow chỉ còn giữ ưu thế duy nhất về tuổi đời và số lượng connector có sẵn. Trên toàn bộ các khía cạnh về năng suất lập trình, khả năng kiểm thử, độ tin cậy dữ liệu và kiến trúc đám mây On-Premise, Dagster đều vượt trội hoàn toàn."

---

## SLIDE 15: KHI NÀO DÙNG AI? (ĐỊNH VỊ ỨNG DỤNG DOANH NGHIỆP)

```text
               NÊN CHỌN AIRFLOW                         NÊN CHỌN DAGSTER
     ┌────────────────────────────────────┐   ┌────────────────────────────────────┐
     │ • Điều phối hạ tầng chung chung    │   │ • Nền tảng Dữ liệu & AI/LLM        │
     │ • Bật/tắt máy ảo, trigger job dbt  │   │ • Xử lý văn bản, OCR, Tài chính    │
     │ • Doanh nghiệp có sẵn hạ tầng cũ   │   │ • Cần kiểm thử tự động CI/CD chuẩn │
     │ • Đội ngũ quen với mô hình Cronjob │   │ • Dữ liệu cần truy xuất nguồn gốc  │
     └────────────────────────────────────┘   └────────────────────────────────────┘
```

* **Khuyến nghị cho dự án thay thế AWS Step Functions**:
  * Vì hệ thống cũ của chúng ta xử lý **nghiệp vụ tài chính, OCR chứng từ và kiểm tra điều kiện**, mô hình của Dagster khớp 100% với tư duy luân chuyển trạng thái của Step Functions nhưng mang lại khả năng mở rộng không giới hạn trên hạ tầng On-Premise.

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Chúng tôi không nói Airflow tệ. Nếu công ty chỉ cần một công cụ kích hoạt dbt hay chạy job Spark hàng đêm, Airflow vẫn dùng tốt. 
> Nhưng với bài toán thay thế AWS Step Functions trên On-Premise: xử lý OCR văn bản, phân loại hồ sơ và kiểm soát rủi ro tài chính, **Dagster chính là sự lựa chọn số 1 của tương lai**."

---

## SLIDE 16: LỘ TRÌNH TRIỂN KHAI 3 GIAI ĐOẠN (MIGRATION ROADMAP)

* **Giai đoạn 1: Chuẩn hóa & Thử nghiệm (Tháng 1 - 2)**
  * Dựng cụm Dagster trên Kubernetes On-Premise (Helm chart chuẩn).
  * Di chuyển 2 pipeline trọng điểm: OCR Hóa đơn PDF & Báo cáo đối soát chi phí.
* **Giai đoạn 2: Tích hợp CI/CD & Data Quality (Tháng 3 - 4)**
  * Áp dụng bộ Unit Test `pytest` tự động vào quy trình Git push.
  * Cấu hình I/O Manager kết nối cụm lưu trữ MinIO On-Premise.
* **Giai đoạn 3: Chuyển dịch toàn diện & Tắt AWS Step Functions (Tháng 5 - 6)**
  * Chuyển toàn bộ 100% các luồng nghiệp vụ còn lại về On-Premise.
  * Tiết kiệm 65% chi phí vận hành hàng tháng so với trả phí Pay-as-you-go trên AWS.

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Lộ trình di chuyển được thiết kế an toàn trong 3 giai đoạn, không gây gián đoạn hệ thống hiện tại. Việc chuyển dịch này vừa giúp doanh nghiệp làm chủ dữ liệu trên On-Premise, vừa nâng cao chất lượng code của đội ngũ kỹ sư lên chuẩn mực kỹ nghệ phần mềm chuyên nghiệp."

---

## SLIDE 17: TỔNG KẾT & Q&A
### **Cảm Ơn Ban Lãnh Đạo & Các Đồng Nghiệp!**

* **Mã nguồn Demo & Tài liệu**: 
  * Repository: `Airflow_Dagster`
  * Airflow DAG: [invoice_multipage_pdf_dag.py](file:///home/ducdm3/Self_training/AirFlow_Dagster/airflow_demo/dags/invoice_multipage_pdf_dag.py)
  * Dagster Assets: [assets.py](file:///home/ducdm3/Self_training/AirFlow_Dagster/dagster_demo/invoice_processing/assets.py)
  * Unit Tests: [test_invoice_processing.py](file:///home/ducdm3/Self_training/AirFlow_Dagster/dagster_demo/tests/test_invoice_processing.py)
* **Sẵn sàng giải đáp thắc mắc (Q&A)**.

---
**🎙️ Lời thoại diễn giả (Speaker Notes):**
> "Xin trân trọng cảm ơn mọi người đã chú ý lắng nghe. Xin mời các anh chị đặt câu hỏi hoặc yêu cầu demo trực tiếp vào bất kỳ đoạn code nào!"
