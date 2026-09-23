import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

def update_slide7():
    pptx_path = "Airflow_vs_Dagster_Thuyet_Trinh.pptx.pptx"
    prs = Presentation(pptx_path)
    
    # Slide dimensions: 20.0" x 11.25"
    slide_width = prs.slide_width
    slide_height = prs.slide_height
    
    # Color palette
    BG_COLOR = RGBColor(7, 5, 14)          # #07050e
    CARD_BG = RGBColor(18, 14, 32)         # #120e20
    CARD_BG_ALT = RGBColor(15, 23, 42)     # #0f172a
    ACCENT_CYAN = RGBColor(56, 189, 248)   # #38bdf8
    ACCENT_PURPLE = RGBColor(192, 132, 252)# #c084fc
    ACCENT_GREEN = RGBColor(34, 197, 94)   # #22c55e
    ACCENT_ROSE = RGBColor(244, 63, 94)    # #f43f5e
    ACCENT_AMBER = RGBColor(245, 158, 11)  # #f59e0b
    BORDER_PURPLE = RGBColor(88, 28, 135)  # #581c87
    BORDER_CYAN = RGBColor(14, 116, 144)   # #0e7490
    BORDER_SUBTLE = RGBColor(39, 31, 61)   # #271f3d
    TEXT_MAIN = RGBColor(248, 250, 252)    # #f8fafc
    TEXT_MUTED = RGBColor(148, 163, 184)   # #94a3b8
    FONT_MAIN = "Arial"

    # Slide 7 is index 6
    s7 = prs.slides[6]
    
    # Remove all existing shapes on slide 7
    # Note: deleting shapes in reverse order
    for shape in list(s7.shapes):
        sp = shape._element
        sp.getparent().remove(sp)
        
    # Helper: Set slide background
    bg = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, slide_width, slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_COLOR
    bg.line.fill.background()

    # Helper: Card creation
    def create_card(x, y, w, h, border_color=BORDER_PURPLE, bg_color=CARD_BG, border_width=1.5, radius=0.05):
        card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
        card.adjustments[0] = radius
        return card

    # 1. Header (Standardized matching Slide 2 & 3)
    badge = create_card(Inches(0.98), Inches(0.38), Inches(3.6), Inches(0.48),
                        border_color=BORDER_PURPLE, bg_color=CARD_BG, border_width=1.0, radius=0.5)
    tf_b = badge.text_frame
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = Inches(0)
    p_b = tf_b.paragraphs[0]
    p_b.text = "TRIỂN KHAI & VẬN HÀNH"
    p_b.font.name = FONT_MAIN
    p_b.font.size = Pt(11.5)
    p_b.font.bold = True
    p_b.font.color.rgb = ACCENT_PURPLE
    p_b.alignment = PP_ALIGN.CENTER

    title_box = s7.shapes.add_textbox(Inches(4.88), Inches(0.32), Inches(14.2), Inches(0.55))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = Inches(0)
    p_t = tf_t.paragraphs[0]
    p_t.text = "HẠ TẦNG ON-PREMISE & NĂNG LỰC KIỂM THỬ CI/CD"
    p_t.font.name = FONT_MAIN
    p_t.font.size = Pt(24)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_MAIN

    p_sub = tf_t.add_paragraph()
    p_sub.text = "Kiến trúc cụm On-Premise (Kubernetes, MinIO, PostgreSQL) và Năng lực kiểm thử In-Memory tự động"
    p_sub.font.name = FONT_MAIN
    p_sub.font.size = Pt(13)
    p_sub.font.color.rgb = ACCENT_CYAN
    p_sub.space_before = Pt(4)

    # 2. Geometry for 2 Columns
    col_w = Inches(8.75)
    gap = Inches(0.54)
    c1_x = Inches(0.98)
    c2_x = c1_x + col_w + gap
    content_y = Inches(1.42)
    content_h = Inches(9.30)

    # ================= LEFT COLUMN: INFRASTRUCTURE =================
    left_card = create_card(c1_x, content_y, col_w, content_h, border_color=ACCENT_CYAN, border_width=1.5, radius=0.05)
    tf_lc = left_card.text_frame
    tf_lc.word_wrap = True
    tf_lc.margin_left = Inches(0.35)
    tf_lc.margin_right = Inches(0.35)
    tf_lc.margin_top = Inches(0.30)
    tf_lc.margin_bottom = Inches(0.25)

    p = tf_lc.paragraphs[0]
    p.text = "🏢 KIẾN TRÚC HẠ TẦNG ON-PREMISE"
    p.font.name = FONT_MAIN
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    # Sub-card 1: Airflow Infra
    sub1_w = col_w - Inches(0.70)
    sub1_x = c1_x + Inches(0.35)
    sub1_y = content_y + Inches(0.85)
    sub1_h = Inches(2.45)
    sc1 = create_card(sub1_x, sub1_y, sub1_w, sub1_h, border_color=ACCENT_ROSE, bg_color=CARD_BG_ALT, border_width=1.0, radius=0.05)
    tf_s1 = sc1.text_frame
    tf_s1.word_wrap = True
    tf_s1.margin_left = Inches(0.25); tf_s1.margin_right = Inches(0.25)
    tf_s1.margin_top = Inches(0.18); tf_s1.margin_bottom = Inches(0.15)
    p1 = tf_s1.paragraphs[0]
    p1.text = "🔴 AIRFLOW: 6 THÀNH PHẦN RỜI RẠC (CỒNG KỀNH & DỄ NGHẼN)"
    p1.font.name = FONT_MAIN
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = ACCENT_ROSE

    for b_title, b_desc in [
        ("Cụm phân tán phức tạp:", "Scheduler + Celery Workers + Redis Queue + Postgres HA + Webserver + Triggerer."),
        ("Nỗi đau ổ đĩa chia sẻ:", "Bắt buộc dựng NFS/EFS đồng bộ thư mục dags/ giữa các node, nguy cơ nghẽn IOPS."),
        ("Xung đột package Python:", "Mọi task dùng chung môi trường; nâng cấp thư viện dễ gây gãy pipeline khác.")
    ]:
        pt = tf_s1.add_paragraph()
        pt.text = f"• {b_title} "
        pt.font.name = FONT_MAIN
        pt.font.bold = True
        pt.font.size = Pt(11)
        pt.font.color.rgb = TEXT_MAIN
        pt.space_before = Pt(6)
        pr = pt.add_run()
        pr.text = b_desc
        pr.font.bold = False
        pr.font.color.rgb = TEXT_MUTED

    # Sub-card 2: Dagster Infra
    sub2_y = sub1_y + sub1_h + Inches(0.20)
    sub2_h = Inches(2.65)
    sc2 = create_card(sub1_x, sub2_y, sub1_w, sub2_h, border_color=ACCENT_GREEN, bg_color=CARD_BG_ALT, border_width=1.0, radius=0.05)
    tf_s2 = sc2.text_frame
    tf_s2.word_wrap = True
    tf_s2.margin_left = Inches(0.25); tf_s2.margin_right = Inches(0.25)
    tf_s2.margin_top = Inches(0.18); tf_s2.margin_bottom = Inches(0.15)
    p2 = tf_s2.paragraphs[0]
    p2.text = "🟢 DAGSTER: CHUẨN KUBERNETES & CLOUD-NATIVE (TINH GỌN & ĐỘC LẬP)"
    p2.font.name = FONT_MAIN
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_GREEN

    for b_title, b_desc in [
        ("Stack tinh gọn 3 dịch vụ:", "Chỉ cần Dagster Webserver + Daemon + PostgreSQL HA (chỉ lưu event metadata nhẹ)."),
        ("Lưu trữ MinIO S3-Compatible:", "Thay thế hoàn hảo AWS S3 cho PDF hóa đơn và artifacts, I/O Manager tự đẩy/kéo."),
        ("Code Location Pods cách ly:", "Đóng gói Docker riêng, giao tiếp gRPC độc lập; tự do chạy đa phiên bản Python.")
    ]:
        pt = tf_s2.add_paragraph()
        pt.text = f"• {b_title} "
        pt.font.name = FONT_MAIN
        pt.font.bold = True
        pt.font.size = Pt(11)
        pt.font.color.rgb = TEXT_MAIN
        pt.space_before = Pt(6)
        pr = pt.add_run()
        pr.text = b_desc
        pr.font.bold = False
        pr.font.color.rgb = TEXT_MUTED

    # Sub-card 3: Airflow Positioning Summary
    sub3_y = sub2_y + sub2_h + Inches(0.20)
    sub3_h = Inches(2.75)
    sc3 = create_card(sub1_x, sub3_y, sub1_w, sub3_h, border_color=BORDER_CYAN, bg_color=CARD_BG_ALT, border_width=1.0, radius=0.05)
    tf_s3 = sc3.text_frame
    tf_s3.word_wrap = True
    tf_s3.margin_left = Inches(0.25); tf_s3.margin_right = Inches(0.25)
    tf_s3.margin_top = Inches(0.18); tf_s3.margin_bottom = Inches(0.15)
    p3 = tf_s3.paragraphs[0]
    p3.text = "🎯 ĐỊNH VỊ NỀN TẢNG: KHI NÀO NÊN CHỌN AIRFLOW?"
    p3.font.name = FONT_MAIN
    p3.font.size = Pt(13)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_CYAN

    for b_title, b_desc in [
        ("Điều phối hạ tầng chung (Infra Orchestration):", "Bật/tắt cụm VM, dbt snapshot, Spark batch, gửi cảnh báo."),
        ("Đã có sẵn cụm On-Premise ổn định:", "Đội ngũ DevOps đã làm chủ Celery, NFS và quy trình quản trị có sẵn."),
        ("Khuyến nghị:", "Giữ nguyên Airflow cho các tác vụ điều phối hệ thống cấp cao và hạ tầng cũ.")
    ]:
        pt = tf_s3.add_paragraph()
        pt.text = f"• {b_title} "
        pt.font.name = FONT_MAIN
        pt.font.bold = True
        pt.font.size = Pt(11)
        pt.font.color.rgb = TEXT_MAIN
        pt.space_before = Pt(6)
        pr = pt.add_run()
        pr.text = b_desc
        pr.font.bold = False
        pr.font.color.rgb = TEXT_MUTED

    # ================= RIGHT COLUMN: CI/CD & TESTING =================
    right_card = create_card(c2_x, content_y, col_w, content_h, border_color=ACCENT_PURPLE, border_width=1.5, radius=0.05)
    tf_rc = right_card.text_frame
    tf_rc.word_wrap = True
    tf_rc.margin_left = Inches(0.35)
    tf_rc.margin_right = Inches(0.35)
    tf_rc.margin_top = Inches(0.30)
    tf_rc.margin_bottom = Inches(0.25)

    p = tf_rc.paragraphs[0]
    p.text = "⚡ NĂNG LỰC KIỂM THỬ CI/CD & DEVELOPER UX"
    p.font.name = FONT_MAIN
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE

    # Sub-card R1: Airflow Testing Limitations
    sc_r1 = create_card(c2_x + Inches(0.35), sub1_y, sub1_w, sub1_h, border_color=ACCENT_AMBER, bg_color=CARD_BG_ALT, border_width=1.0, radius=0.05)
    tf_r1 = sc_r1.text_frame
    tf_r1.word_wrap = True
    tf_r1.margin_left = Inches(0.25); tf_r1.margin_right = Inches(0.25)
    tf_r1.margin_top = Inches(0.18); tf_r1.margin_bottom = Inches(0.15)
    pr1 = tf_r1.paragraphs[0]
    pr1.text = "⚠️ AIRFLOW: RÀO CẢN LỚN KHI VIẾT UNIT TEST & CI/CD"
    pr1.font.name = FONT_MAIN
    pr1.font.size = Pt(13)
    pr1.font.bold = True
    pr1.font.color.rgb = ACCENT_AMBER

    for b_title, b_desc in [
        ("Dính chặt context & Database:", "Task gắn chặt ti, context, dag_run; cực kỳ khó mock dữ liệu cục bộ."),
        ("Chu kỳ phản hồi chậm (3-5 phút):", "Cần khởi động Docker Compose và migrate SQLite/Postgres để chạy test."),
        ("Hạn chế kiểm thử CI/CD:", "Thời gian kiểm thử kéo dài khiến team ngại viết test trước khi merge mã nguồn.")
    ]:
        pt = tf_r1.add_paragraph()
        pt.text = f"• {b_title} "
        pt.font.name = FONT_MAIN
        pt.font.bold = True
        pt.font.size = Pt(11)
        pt.font.color.rgb = TEXT_MAIN
        pt.space_before = Pt(6)
        pr = pt.add_run()
        pr.text = b_desc
        pr.font.bold = False
        pr.font.color.rgb = TEXT_MUTED

    # Sub-card R2: Dagster Testing Superpower
    sc_r2 = create_card(c2_x + Inches(0.35), sub2_y, sub1_w, sub2_h, border_color=ACCENT_GREEN, bg_color=CARD_BG_ALT, border_width=1.0, radius=0.05)
    tf_r2 = sc_r2.text_frame
    tf_r2.word_wrap = True
    tf_r2.margin_left = Inches(0.25); tf_r2.margin_right = Inches(0.25)
    tf_r2.margin_top = Inches(0.18); tf_r2.margin_bottom = Inches(0.15)
    pr2 = tf_r2.paragraphs[0]
    pr2.text = "💎 DAGSTER: UNIT TEST TRONG RAM 0.12S (PYTEST IN-MEMORY)"
    pr2.font.name = FONT_MAIN
    pr2.font.size = Pt(13)
    pr2.font.bold = True
    pr2.font.color.rgb = ACCENT_GREEN

    for b_title, b_desc in [
        ("In-Memory Testing thuần khiết:", "Hàm Asset là pure Python; materialize([asset]) trong RAM không cần database."),
        ("Asset Checks chặn đứng lỗi (0.02s):", "@asset_check(blocking=True) ngắt cầu dao ngay nếu hóa đơn vượt 100M."),
        ("Tự động hóa CI/CD hoàn hảo:", "Tích hợp mượt mà pytest vào GitLab CI / GitHub Actions trên từng Pull Request.")
    ]:
        pt = tf_r2.add_paragraph()
        pt.text = f"• {b_title} "
        pt.font.name = FONT_MAIN
        pt.font.bold = True
        pt.font.size = Pt(11)
        pt.font.color.rgb = TEXT_MAIN
        pt.space_before = Pt(6)
        pr = pt.add_run()
        pr.text = b_desc
        pr.font.bold = False
        pr.font.color.rgb = TEXT_MUTED

    # Sub-card R3: Dagster Positioning Summary
    sc_r3 = create_card(c2_x + Inches(0.35), sub3_y, sub1_w, sub3_h, border_color=BORDER_PURPLE, bg_color=CARD_BG_ALT, border_width=1.0, radius=0.05)
    tf_r3 = sc_r3.text_frame
    tf_r3.word_wrap = True
    tf_r3.margin_left = Inches(0.25); tf_r3.margin_right = Inches(0.25)
    tf_r3.margin_top = Inches(0.18); tf_r3.margin_bottom = Inches(0.15)
    pr3 = tf_r3.paragraphs[0]
    pr3.text = "🚀 ĐỊNH VỊ NỀN TẢNG: KHI NÀO NÊN CHỌN DAGSTER?"
    pr3.font.name = FONT_MAIN
    pr3.font.size = Pt(13)
    pr3.font.bold = True
    pr3.font.color.rgb = ACCENT_PURPLE

    for b_title, b_desc in [
        ("Thay thế AWS Step Functions On-Premise:", "Xử lý hồ sơ đa trang, OCR và luồng kiểm toán tài chính phức tạp."),
        ("Xây dựng Modern Data Platform:", "Quản trị Data Lineage, phân tách môi trường dev/staging/prod bằng gRPC."),
        ("Đề xuất:", "Chọn Dagster làm nền tảng chuẩn hóa dữ liệu chiến lược thế hệ mới của doanh nghiệp!")
    ]:
        pt = tf_r3.add_paragraph()
        pt.text = f"• {b_title} "
        pt.font.name = FONT_MAIN
        pt.font.bold = True
        pt.font.size = Pt(11)
        pt.font.color.rgb = TEXT_MAIN
        pt.space_before = Pt(6)
        pr = pt.add_run()
        pr.text = b_desc
        pr.font.bold = False
        pr.font.color.rgb = TEXT_MUTED

    # Speaker notes
    notes_slide = s7.notes_slide
    tf_n = notes_slide.notes_text_frame
    tf_n.text = "Speaker Note: Slide 7 phân tích toàn diện 2 khía cạnh: (1) Kiến trúc hạ tầng On-Premise (Airflow 6 thành phần vs Dagster K8s tinh gọn); (2) Tốc độ kiểm thử CI/CD (Airflow 3-5 phút vs Dagster in-memory 0.12s); và kết luận định vị khi nào chọn Airflow vs Dagster."

    prs.save(pptx_path)
    print(f"Successfully updated Slide 7 in {pptx_path}!")

if __name__ == "__main__":
    update_slide7()
