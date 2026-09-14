# Dàn Ý Bài Thuyết Trình: Chuyển Dịch Workflow Orchestration từ AWS Step Functions sang On-Premise (Airflow vs. Dagster)

> **Tên bài thuyết trình gợi ý:**
> *Tiếng Việt:* Hành trình On-Premise Orchestration: Chuyển dịch từ AWS Step Functions sang Apache Airflow hay Dagster?  
> *Tiếng Anh:* Modernizing Workflow Orchestration: Migrating from AWS Step Functions to On-Premise with Airflow vs. Dagster  
> **Thời lượng dự kiến:** 35 - 45 phút (bao gồm Q&A)  
> **Đối tượng lắng nghe:** CTO, Engineering Manager, Tech Lead, Data Engineer, DevOps/SRE.

---

## MỤC LỤC TRÌNH BÀY

1. **Phần 1: Bối cảnh & Động lực chuyển dịch** (Slide 1 - 2)
2. **Phần 2: Thách thức khi rời bỏ AWS Step Functions** (Slide 3)
3. **Phần 3: Giới thiệu ứng cử viên: Apache Airflow vs. Dagster** (Slide 4)
4. **Phần 4: So sánh chuyên sâu & Ánh xạ logic (Mental Model Mapping)** (Slide 5 - 7)
5. **Phần 5: Thiết kế kiến trúc On-Premise & Lộ trình di chuyển** (Slide 8 - 9)
6. **Phần 6: Ma trận đánh giá & Khuyến nghị quyết định** (Slide 10 - 11)
7. **Phần 7: Q&A & Kế hoạch tiếp theo** (Slide 12)

---

## CHI TIẾT TỪNG SLIDE & NỘI DUNG THUYẾT TRÌNH (SPEAKER NOTES)

### SLIDE 1: Hiện Trạng & Lý Do Đã Chọn AWS Step Functions
* **Tiêu đề Slide:** *Hiện trạng: Workflow Orchestration trên AWS Step Functions*
* **Nội dung hiển thị:**
  * Mô hình: Serverless State Machine, viết bằng Amazon States Language (ASL / JSON).
  * Điểm mạnh đã tận dụng:
    * Zero Infrastructure Management (Không cần quản trị server, scheduler hay worker).
    * Tích hợp sâu vào hệ sinh thái AWS (Lambda, ECS/Fargate, Glue, Athena, S3).
    * Visual Workflow Studio trực quan, xem được lịch sử trạng thái từng bước (Step execution history).
* **Lời thoại diễn giả (Speaker Notes):**
  > "Kính thưa các anh chị, trong giai đoạn đầu xây dựng hệ thống trên Cloud, AWS Step Functions là lựa chọn hiển nhiên giúp đội ngũ phát triển nhanh chóng kết nối các dịch vụ serverless như Lambda hay ECS mà không tốn công quản trị hạ tầng. Tuy nhiên, khi quy mô dữ liệu và số lượng quy trình tăng lên, chúng ta bắt đầu gặp phải các rào cản lớn về chi phí và tính linh hoạt."

---

### SLIDE 2: Tại Sao Phải Di Chuyển Về On-Premise?
* **Tiêu đề Slide:** *Động lực chuyển dịch: Bài toán On-Premise*
* **Nội dung hiển thị:**
  * **Tối ưu chi phí (Cost Efficiency):** Step Functions tính phí theo State Transition; chi phí tăng lũy tiến khi quy mô pipeline chạy liên tục 24/7.
  * **Tuân thủ & Bảo mật dữ liệu (Compliance & Data Sovereignty):** Yêu cầu lưu trữ và xử lý dữ liệu nhạy cảm bên trong mạng nội bộ (On-Premise Private Datacenter).
  * **Tận dụng hạ tầng sẵn có:** Doanh nghiệp đã đầu tư hạ tầng phần cứng, Private Cloud (Kubernetes Cluster) cần được tối đa hóa hiệu suất sử dụng.
  * **Tránh Vendor Lock-in:** ASL chỉ chạy được trên AWS, khó đem sang môi trường hybrid hoặc multi-cloud.
* **Lời thoại diễn giả (Speaker Notes):**
  > "Việc chuyển dịch về On-premise không chỉ đơn thuần là bài toán cắt giảm hóa đơn AWS hàng tháng, mà còn là chiến lược tự chủ dữ liệu, bảo mật và tận dụng cụm hạ tầng server nội bộ đã được đầu tư."

---

### SLIDE 3: Thách Thức Khi Rời Khỏi Step Functions
* **Tiêu đề Slide:** *Thách thức khi chuyển từ Serverless sang On-Premise*
* **Nội dung hiển thị:**
  * ❌ Mất đi tính năng Fully-Managed: Phải tự dựng và vận hành Scheduler, Queue, Database, Worker, UI.
  * ❌ Quản lý State & Storage: Cần giải pháp lưu trạng thái workflow và data passing thay thế cho AWS engine nội bộ.
  * ❌ Chuyển đổi ngôn ngữ: Chuyển từ JSON declarative (ASL) sang Code-as-Configuration (Python).
  * ❌ Độ sẵn sàng cao (High Availability): Phải tự thiết kế giải pháp Failover, Autoscaling, Disaster Recovery trên On-premise K8s/Bare-metal.
* **Lời thoại diễn giả (Speaker Notes):**
  > "Khi rời Step Functions, chúng ta được tự do nhưng phải gánh vác trách nhiệm vận hành. Câu hỏi đặt ra là: Công cụ mã nguồn mở nào vừa mạnh mẽ để chạy on-premise, vừa giảm thiểu tối đa gánh nặng vận hành cho đội ngũ?"

---

### SLIDE 4: Giới Thiệu Ứng Cử Viên: Apache Airflow & Dagster
* **Tiêu đề Slide:** *Hai trường phái Orchestration On-Premise*
* **Nội dung hiển thị:**
  * **Apache Airflow ("Vị vua tiền nhiệm" - Task-Centric):**
    * Ra đời năm 2014 (Airbnb), là tiêu chuẩn công nghiệp (De-facto standard).
    * Triết lý: Tập trung vào **Task** ("Làm cái gì và theo thứ tự nào?").
    * Hệ sinh thái khổng lồ, hàng trăm Providers/Operators có sẵn.
  * **Dagster ("Thế hệ kế cận" - Data/Asset-Centric):**
    * Ra đời năm 2018 (sáng lập bởi cựu tác giả GraphQL tại Facebook).
    * Triết lý: Tập trung vào **Data Asset** ("Dữ liệu nào cần sinh ra và trạng thái của nó ra sao?").
    * Thiết kế sinh ra cho Data Platform hiện đại, hỗ trợ Local Testing và Data Lineage vượt trội.
* **Lời thoại diễn giả (Speaker Notes):**
  > "Airflow là công cụ quen thuộc nhất với hầu hết kỹ sư dữ liệu. Trong khi đó, Dagster là một cách tiếp cận hoàn toàn mới, giải quyết đúng những điểm yếu cốt tử của các orchestrator thế hệ cũ."

---

### SLIDE 5: Ánh Xạ Khái Niệm (Mental Model Mapping)
* **Tiêu đề Slide:** *Chuyển dịch tư duy: Step Functions vs. Airflow vs. Dagster*
* **Nội dung bảng so sánh:**

| Khái niệm AWS Step Functions | Tương đương trong Apache Airflow | Tương đương trong Dagster |
| :--- | :--- | :--- |
| **State Machine Definition** | Python DAG file | Job / Definitions (Repository) |
| **Task State (Lambda/ECS/Glue)** | Operator (`PythonOperator`, `KubernetesPodOperator`) | `@op` hoặc `@asset` (Compute function) |
| **Choice State (Branching)** | `BranchPythonOperator` | Conditional Output / Branching |
| **Map State (Dynamic Parallel)** | Dynamic Task Mapping (`.expand()`) | Dynamic Outputs / Partitioned Asset |
| **State Input/Output JSON** | Airflow XCom (Metadata) | Dagster `IOManager` (Type-safe & Persistent) |
| **Execution History & Retries** | Task Instance State, Grid View | Run Timeline, Step Events, Asset History |

* **Lời thoại diễn giả (Speaker Notes):**
  > "Điểm khác biệt quan trọng nhất ở đây là việc truyền dữ liệu giữa các bước. Trong Step Functions, ta truyền JSON payload qua lại. Trong Airflow, XCom chỉ nên chứa metadata nhỏ. Còn trong Dagster, IOManager tự động quản lý việc lưu và đọc dữ liệu giữa các bước vào MinIO hoặc disk một cách trong suốt."

---

### SLIDE 6: So Sánh Chuyên Sâu: Trải Nghiệm Lập Trình & Kiểm Thử (DevX)
* **Tiêu đề Slide:** *Developer Experience & Testing: Nỗi đau lớn nhất của Step Functions*
* **Nội dung hiển thị:**
  * **AWS Step Functions:** Khó test local nhất; thường phải deploy lên AWS dev account để test, tốn thời gian feedback loop.
  * **Apache Airflow:**
    * Viết code Python linh hoạt nhưng test DAG logic local cần docker-compose hoặc Airflow Breeze khá cồng kềnh.
    * Thường chỉ test được cú pháp DAG, khó mock data/operator chạy offline hoàn toàn.
  * **Dagster (Điểm sáng vượt trội):**
    * Được thiết kế từ đầu hỗ trợ Unit Testing với `pytest`.
    * Chạy thử và debug trực tiếp trên máy cá nhân không cần dựng cụm dịch vụ phụ trợ.
    * Hỗ trợ mock Resource và Mock IOManager cực kỳ trực quan.
* **Lời thoại diễn giả (Speaker Notes):**
  > "Một trong những điểm ức chế nhất của kỹ sư khi làm việc với Step Functions là không thể test nhanh trên máy local. Ở khía cạnh này, Dagster đem lại trải nghiệm phát triển phần mềm chuẩn mực (Software Engineering Best Practices) hơn hẳn Airflow."

---

### SLIDE 7: So Sánh Vận Hành & Khả Năng Mở Rộng On-Premise (Ops & Scalability)
* **Tiêu đề Slide:** *Vận hành hạ tầng On-Premise: Airflow vs. Dagster*
* **Nội dung hiển thị:**
  * **Kiến trúc thành phần:**
    * *Airflow:* Scheduler, Webserver, Triggerer, Metadata DB (PostgreSQL), Message Broker (Redis/RabbitMQ nếu dùng Celery).
    * *Dagster:* Webserver (Dagit), Daemon (Scheduler, Sensor, Run Coordinator), Metadata DB (PostgreSQL), Code Location Servers (gRPC containers).
  * **Triển khai trên Kubernetes:**
    * Cả hai đều có **Official Helm Chart** tiêu chuẩn production.
    * Dagster tách biệt hoàn toàn Control Plane (Daemon/Webserver) và User Code (Code Location). Lỗi code của developer không làm crash hệ thống điều phối chung.
    * Airflow KubernetesExecutor khởi tạo Pod cho mỗi task, cách ly tốt nhưng overhead khởi tạo pod cần lưu ý.
* **Lời thoại diễn giả (Speaker Notes):**
  > "Về mặt Ops, Dagster có kiến trúc hiện đại khi tách biệt User Code ra khỏi System Core thông qua gRPC. Nếu một data pipeline bị lỗi dependencies hay crash memory, giao diện và scheduler của Dagster vẫn chạy bình thường."

---

### SLIDE 8: Kiến Trúc Mục Tiêu Đề Xuất Trên On-Premise (Target Architecture)
* **Tiêu đề Slide:** *Thiết kế kiến trúc On-Premise Orchestration trên Kubernetes*
* **Sơ đồ kiến trúc (Text Diagram):**
  ```text
  [ Client / Users / Data Engineers ]
                 │
                 ▼
  [ Ingress Controller (TLS / SSO Authentication) ]
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
  [ Web UI / Dashboard ] [ Scheduler / Daemon ]
      │                     │
      ├─────────────────────┼─────────────────────┐
      ▼                     ▼                     ▼
  [ PostgreSQL HA ]   [ MinIO Cluster ]    [ K8s Task Pods ]
  (State & Metadata)  (Thay thế S3/Data)   (User Compute)
  ```
* **Nội dung hiển thị:**
  * **Compute Plane:** Kubernetes Cluster nội bộ chạy task pods cách ly.
  * **Storage Plane:** MinIO Cluster phân tán chuẩn S3 API (lưu log, artifact, intermediate data).
  * **State Plane:** PostgreSQL Cluster với giải pháp HA (Patroni / CloudNative-PG).
  * **Observability:** Tích hợp Prometheus metrics + Grafana Dashboards + Alerting webhook.

---

### SLIDE 9: Lộ Trình Chuyển Đổi (Migration Roadmap)
* **Tiêu đề Slide:** *Kế hoạch di chuyển 3 giai đoạn (Safe & Zero-Downtime)*
* **Nội dung hiển thị:**
  * **Phase 1: Chuẩn bị & PoC (Tuần 1 - 4):**
    * Dựng cụm Kubernetes On-premise + MinIO + Postgres.
    * Cài đặt Orchestrator được chọn bằng Helm Chart.
    * Chuyển đổi thử nghiệm 1-2 Step Functions tiêu biểu (1 batch đơn giản, 1 pipeline phức tạp có Map/Branching).
  * **Phase 2: Chạy song song (Parallel Run) & Đánh giá (Tuần 5 - 8):**
    * Chạy song song cả AWS Step Functions và On-Premise.
    * Kiểm tra tính toàn vẹn dữ liệu, đo lường độ trễ (latency), khả năng chịu tải và kịch bản phục hồi sự cố.
  * **Phase 3: Chuyển đổi chính thức & Tắt Cloud (Tuần 9 - 12):**
    * Chuyển toàn bộ trigger lịch trình sang On-premise.
    * Ngắt kết nối, lưu trữ mã nguồn ASL cũ và xóa tài nguyên trên AWS để ngắt chi phí.

---

### SLIDE 10: Ma Trận Đánh Giá Tổng Thể (Decision Matrix)
* **Tiêu đề Slide:** *Ma trận so sánh quyết định*
* **Bảng chấm điểm (Thang điểm 10):**

| Tiêu chí | Trọng số | AWS Step Functions | Apache Airflow | Dagster |
| :--- | :---: | :---: | :---: | :---: |
| **Chi phí vận hành dài hạn (Hardware/Licensing)** | 20% | 5/10 (Đắt khi scale) | **9/10** (Open-source) | **9/10** (Open-source) |
| **Trải nghiệm Local Dev & Testing** | 20% | 4/10 | 6.5/10 | **9.5/10** |
| **Độ ổn định & Cộng đồng / Tuyển dụng** | 15% | 8/10 | **9.5/10** | 7.5/10 |
| **Khả năng quản lý luân chuyển Data/State** | 15% | 7/10 (Giới hạn 256KB) | 6.5/10 | **9.5/10** (Native I/O) |
| **Độ dễ dàng triển khai On-Prem K8s** | 15% | 0/10 (Không hỗ trợ) | 8.5/10 | **9/10** |
| **Khả năng quan sát (Data Lineage / Asset Catalog)**| 15% | 7/10 | 6.5/10 | **9.5/10** |
| **TỔNG ĐIỂM CÓ TRỌNG SỐ** | **100%** | **5.25** | **7.75** | **8.95** |

---

### SLIDE 11: Khuyến Nghị & Đề Xuất (Recommendation)
* **Tiêu đề Slide:** *Chúng ta nên chọn công cụ nào?*
* **Nội dung hiển thị:**
  * 💡 **Trường hợp khuyến nghị chọn Apache Airflow:**
    * Đội ngũ hiện tại đã có nhiều năm kinh nghiệm viết và vận hành Airflow.
    * Pipeline phần lớn là điều phối tác vụ chung (Generic task orchestration: trigger bash script, restart server, chạy batch job đơn thuần không liên quan mật thiết đến cấu trúc data).
  * 💡 **Trường hợp khuyến nghị chọn Dagster (ĐỀ XUẤT CHÍNH):**
    * Bạn muốn khắc phục triệt để điểm yếu lớn nhất của Step Functions: **Khả năng test và debug local**.
    * Workload là **Data Pipelines / Analytics / ML**: Dagster hiểu rõ tài sản dữ liệu (Asset), tự động hóa lineage, theo dõi data freshness.
    * Kiến trúc phân tách User Code của Dagster giúp hệ thống on-premise ổn định, ít xung đột thư viện giữa các team.
* **Lời thoại diễn giả (Speaker Notes):**
  > "Nếu mục tiêu của chúng ta chỉ là tìm một công cụ chạy thay thế với lực lượng sẵn có thì Airflow là lựa chọn an toàn. Nhưng nếu chúng ta muốn nâng cấp toàn diện năng lực kỹ thuật dữ liệu, hiện đại hóa quy trình phát triển và kiểm thử theo chuẩn Software Engineering, Dagster là khoản đầu tư vượt trội cho tương lai."

---

### SLIDE 12: Q&A & Kế Hoạch Tiếp Theo (Action Items)
* **Tiêu đề Slide:** *Hỏi đáp & Bước tiếp theo*
* **Nội dung hiển thị:**
  * Quyết định chốt lựa chọn công cụ giữa các bên liên quan.
  * Phê duyệt tài nguyên cụm máy chủ On-premise cho môi trường PoC (Dự kiến: 3 Master Nodes, 5 Worker Nodes).
  * Phân công nhân sự thực hiện PoC trong 4 tuần tới.
