"""
Script to generate a professional, high-end PowerPoint presentation (.pptx)
directly matching the aesthetic and structure of 'slides copy.html' and 'SLIDES.md'.

Key Design Highlights:
- 100% elimination of dated 3D cylinders/cans (MSO_SHAPE.CAN) and ovals (MSO_SHAPE.OVAL)
- Sleek modern glassmorphism tech aesthetic with rounded rectangle cards
- Deep contrast dark palette matching slides copy.html (#07050e background, #120e20 card)
- High-fidelity recreation of Slide 1 (Keynote Cover Arena), Slide 4 (Dual Architecture Stage),
  and Slide 7 (4-Block Comprehensive Infrastructure & CI/CD Framework)
- Mathematically balanced grids, symmetrical margins, and explicit text frame padding
- 100% preservation of all content, Vietnamese text, metrics, and speaker notes
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # 16:9 Widescreen: 13.333 x 7.5 inches
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Exact Color Palette from slides copy.html (:root CSS)
    BG_COLOR = RGBColor(7, 5, 14)              # --bg-main: #07050e
    CARD_BG = RGBColor(18, 14, 32)             # --bg-card: #120e20
    CARD_BG_ALT = RGBColor(15, 23, 42)         # #0f172a (Dark slate)
    CARD_INNER = RGBColor(26, 20, 48)          # Elevated nested card
    CARD_DARK_SLATE = RGBColor(15, 23, 42)     # Node slate fill

    BORDER_PURPLE = RGBColor(168, 85, 247)     # --border-card: #a855f7
    BORDER_PURPLE_BRIGHT = RGBColor(192, 132, 252) # #c084fc
    BORDER_CYAN = RGBColor(56, 189, 248)       # #38bdf8
    BORDER_SUBTLE = RGBColor(40, 32, 65)       # Subtle card line

    ACCENT_CYAN = RGBColor(56, 189, 248)       # Airflow cyan (#38bdf8)
    ACCENT_BLUE = RGBColor(96, 165, 250)       # #60a5fa
    ACCENT_PURPLE = RGBColor(192, 132, 252)    # Dagster purple (#c084fc)
    ACCENT_PURPLE_DEEP = RGBColor(147, 51, 234)# #9333ea
    ACCENT_GREEN = RGBColor(34, 197, 94)       # Success / Passed (#22c55e)
    ACCENT_GREEN_BG = RGBColor(6, 78, 59)      # #064e3b
    ACCENT_ROSE = RGBColor(244, 63, 94)        # Danger / Error (#f43f5e)
    ACCENT_ROSE_BG = RGBColor(76, 5, 25)       # #4c0519
    ACCENT_AMBER = RGBColor(245, 158, 11)      # Warning / Branch (#f59e0b)
    ACCENT_AMBER_BG = RGBColor(69, 26, 3)      # #451a03

    # Dagster Node Palette (matching Mermaid styles in slides copy.html)
    DG_INDIGO = RGBColor(30, 27, 75)           # fill:#1e1b4b
    DG_INDIGO_BORDER = RGBColor(129, 140, 248) # stroke:#818cf8
    DG_PURPLE_DEEP = RGBColor(46, 16, 101)     # fill:#2e1065
    DG_PURPLE_BORDER = RGBColor(192, 132, 252) # stroke:#c084fc
    DG_ROSE_DEEP = RGBColor(59, 7, 100)        # fill:#3b0764 (Invalid invoice)

    TEXT_MAIN = RGBColor(248, 250, 252)        # #f8fafc
    TEXT_MUTED = RGBColor(148, 163, 184)       # #94a3b8
    TEXT_DIM = RGBColor(100, 116, 139)         # #64748b
    TEXT_CODE = RGBColor(226, 232, 240)        # Monospace / light text

    FONT_MAIN = "Arial"

    def set_slide_background(slide, color=BG_COLOR):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, badge_text, title_text, subtitle_text=""):
        badge_w = min(max(Inches(len(badge_text) * 0.11 + 0.45), Inches(1.8)), Inches(3.6))
        if badge_text:
            badge_box = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.32), badge_w, Inches(0.32)
            )
            badge_box.fill.solid()
            badge_box.fill.fore_color.rgb = CARD_BG
            badge_box.line.color.rgb = BORDER_PURPLE
            badge_box.line.width = Pt(1.2)
            tf = badge_box.text_frame
            tf.word_wrap = False
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf.margin_left = Inches(0.1)
            tf.margin_right = Inches(0.1)
            tf.margin_top = Inches(0.02)
            tf.margin_bottom = Inches(0.02)
            p = tf.paragraphs[0]
            p.text = badge_text.upper()
            p.alignment = PP_ALIGN.CENTER
            p.font.name = FONT_MAIN
            p.font.size = Pt(9.5)
            p.font.bold = True
            p.font.color.rgb = ACCENT_PURPLE

        title_top = Inches(0.68 if badge_text else 0.38)
        title_box = slide.shapes.add_textbox(Inches(0.8), title_top, Inches(11.733), Inches(0.85))
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_left = 0
        tf.margin_right = 0
        tf.margin_top = 0
        tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = FONT_MAIN
        p.font.size = Pt(21)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN

        if subtitle_text:
            p2 = tf.add_paragraph()
            p2.text = subtitle_text
            p2.font.name = FONT_MAIN
            p2.font.size = Pt(11.5)
            p2.font.color.rgb = ACCENT_CYAN
            p2.space_before = Pt(3)

    def add_node_card(slide, x, y, w, h, title, subtitle="", bg_color=CARD_BG, border_color=BORDER_PURPLE,
                      title_color=TEXT_MAIN, sub_color=TEXT_MUTED, title_size=10.5, sub_size=8.8,
                      bold_title=True, border_width=1.2, align=PP_ALIGN.CENTER):
        """Modern flat glassmorphic rounded card replacing all cans/ovals."""
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_width)

        tf = shape.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.08)
        tf.margin_right = Inches(0.08)
        tf.margin_top = Inches(0.04)
        tf.margin_bottom = Inches(0.04)

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_MAIN
        p.font.size = Pt(title_size)
        p.font.bold = bold_title
        p.font.color.rgb = title_color
        p.alignment = align

        if subtitle:
            p2 = tf.add_paragraph()
            p2.text = subtitle
            p2.font.name = FONT_MAIN
            p2.font.size = Pt(sub_size)
            p2.font.color.rgb = sub_color
            p2.alignment = align
            p2.space_before = Pt(2)
        return shape

    def add_arrow_down(slide, x, y, w=Inches(0.4), h=Inches(0.24), text="↓", color=ACCENT_CYAN, font_size=13):
        box = slide.shapes.add_textbox(x, y, w, h)
        tf = box.text_frame
        tf.word_wrap = False
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = 0
        tf.margin_right = 0
        tf.margin_top = 0
        tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = FONT_MAIN
        p.font.size = Pt(font_size)
        p.font.bold = True
        p.font.color.rgb = color
        p.alignment = PP_ALIGN.CENTER
        return box

    def add_arrow_label(slide, x_center, y, text, color=ACCENT_PURPLE, w=Inches(2.6), h=Inches(0.24)):
        x = x_center - (w / 2)
        box = slide.shapes.add_textbox(x, y, w, h)
        tf = box.text_frame
        tf.word_wrap = False
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = 0
        tf.margin_right = 0
        tf.margin_top = 0
        tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = FONT_MAIN
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = color
        p.alignment = PP_ALIGN.CENTER
        return box

    def add_speaker_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # =========================================================================
    # SLIDE 1: COVER ARENA (KEYNOTE STYLE MATCHING slides copy.html)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Top badges matching header in slides copy.html
    top_badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.8), Inches(0.55), Inches(5.733), Inches(0.38))
    top_badge.fill.solid()
    top_badge.fill.fore_color.rgb = CARD_BG
    top_badge.line.color.rgb = BORDER_SUBTLE
    top_badge.line.width = Pt(1)
    tf_tb = top_badge.text_frame
    tf_tb.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_tb = tf_tb.paragraphs[0]
    p_tb.text = "⚡ INVOICE PDF FLAGSHIP SCENARIO   |   🏢 ON-PREMISE / KUBERNETES"
    p_tb.font.name = FONT_MAIN
    p_tb.font.size = Pt(10)
    p_tb.font.bold = True
    p_tb.font.color.rgb = ACCENT_CYAN
    p_tb.alignment = PP_ALIGN.CENTER

    # Main Presentation Title & Subtitle
    title_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.15), Inches(11.333), Inches(1.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "SO SÁNH THỰC CHIẾN: AIRFLOW vs DAGSTER"
    p.font.name = FONT_MAIN
    p.font.size = Pt(35)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = "Chuyên đề: Xử lý Hồ sơ Hóa đơn Đa trang (Invoice PDF Processing) & Chuyển dịch On-Premise"
    p2.font.name = FONT_MAIN
    p2.font.size = Pt(16)
    p2.font.color.rgb = ACCENT_CYAN
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(8)

    # Arena Layout - Sleek Rounded Glass Cards (NO OVALS!)
    card_w = Inches(4.75)
    card_h = Inches(3.1)
    card_y = Inches(3.2)
    c_left_x = Inches(1.2)
    c_right_x = Inches(7.383)

    # Left Card: Airflow Brand
    c_left = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left_x, card_y, card_w, card_h)
    c_left.fill.solid()
    c_left.fill.fore_color.rgb = CARD_BG
    c_left.line.color.rgb = ACCENT_CYAN
    c_left.line.width = Pt(1.8)
    tf_l = c_left.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = Inches(0.28)
    tf_l.margin_right = Inches(0.28)
    tf_l.margin_top = Inches(0.22)
    tf_l.margin_bottom = Inches(0.2)

    p = tf_l.paragraphs[0]
    p.text = "🌪️ APACHE AIRFLOW"
    p.font.name = FONT_MAIN
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.alignment = PP_ALIGN.CENTER

    p_sub_af = tf_l.add_paragraph()
    p_sub_af.text = "Workflow as Code (Task-Centric)"
    p_sub_af.font.name = FONT_MAIN
    p_sub_af.font.size = Pt(11)
    p_sub_af.font.bold = True
    p_sub_af.font.color.rgb = RGBColor(125, 211, 252)
    p_sub_af.alignment = PP_ALIGN.CENTER
    p_sub_af.space_before = Pt(2)

    for b in [
        "• Hệ sinh thái 10+ năm, chuẩn mực công nghiệp",
        "• Điều phối tác vụ định kỳ & tích hợp hạ tầng",
        "• KubernetesExecutor, Celery, RBAC chặt chẽ",
        "• Hàng trăm nhà cung cấp dịch vụ (Providers)"
    ]:
        pb = tf_l.add_paragraph()
        pb.text = b
        pb.font.name = FONT_MAIN
        pb.font.size = Pt(11.2)
        pb.font.color.rgb = TEXT_MUTED
        pb.space_before = Pt(6)

    # Center VS Badge: Modern Rounded Hex/Square Badge (NOT AN OVAL!)
    vs_w = Inches(1.15)
    vs_h = Inches(1.15)
    vs_x = (prs.slide_width - vs_w) / 2
    vs_y = Inches(4.15)
    vs_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, vs_x, vs_y, vs_w, vs_h)
    vs_box.fill.solid()
    vs_box.fill.fore_color.rgb = RGBColor(26, 16, 50)
    vs_box.line.color.rgb = ACCENT_PURPLE
    vs_box.line.width = Pt(2.2)
    tf_vs = vs_box.text_frame
    tf_vs.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf_vs.paragraphs[0]
    p.text = "VS"
    p.font.name = FONT_MAIN
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = RGBColor(243, 232, 255)
    p.alignment = PP_ALIGN.CENTER

    # Right Card: Dagster Brand
    c_right = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_right_x, card_y, card_w, card_h)
    c_right.fill.solid()
    c_right.fill.fore_color.rgb = CARD_BG
    c_right.line.color.rgb = ACCENT_PURPLE
    c_right.line.width = Pt(1.8)
    tf_r = c_right.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = Inches(0.28)
    tf_r.margin_right = Inches(0.28)
    tf_r.margin_top = Inches(0.22)
    tf_r.margin_bottom = Inches(0.2)

    p = tf_r.paragraphs[0]
    p.text = "💎 DAGSTER"
    p.font.name = FONT_MAIN
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.alignment = PP_ALIGN.CENTER

    p_sub_dg = tf_r.add_paragraph()
    p_sub_dg.text = "Data as Code (Asset-Centric)"
    p_sub_dg.font.name = FONT_MAIN
    p_sub_dg.font.size = Pt(11)
    p_sub_dg.font.bold = True
    p_sub_dg.font.color.rgb = RGBColor(216, 180, 254)
    p_sub_dg.alignment = PP_ALIGN.CENTER
    p_sub_dg.space_before = Pt(2)

    for b in [
        "• Tách rời Code Server gRPC & Orchestrator",
        "• Tích hợp kiểm định dữ liệu (Asset Checks)",
        "• Kiểm thử in-memory siêu tốc trong CI/CD (~0.12s)",
        "• Tự động truy vết Data Lineage & I/O Manager"
    ]:
        pb = tf_r.add_paragraph()
        pb.text = b
        pb.font.name = FONT_MAIN
        pb.font.size = Pt(11.2)
        pb.font.color.rgb = TEXT_MUTED
        pb.space_before = Pt(6)

    # Executive Footer
    footer = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(6.58), Inches(9.733), Inches(0.48))
    footer.fill.solid()
    footer.fill.fore_color.rgb = CARD_BG
    footer.line.color.rgb = BORDER_SUBTLE
    footer.line.width = Pt(1)
    tf_ft = footer.text_frame
    tf_ft.vertical_anchor = MSO_ANCHOR.MIDDLE
    ft_p = tf_ft.paragraphs[0]
    ft_p.text = "Khán giả: CTO, Solution Architect, Tech Lead, Data Platform Team   |   Thời lượng: 35-45 phút"
    ft_p.font.name = FONT_MAIN
    ft_p.font.size = Pt(11)
    ft_p.font.color.rgb = TEXT_MUTED
    ft_p.alignment = PP_ALIGN.CENTER

    add_speaker_notes(s1, "Slide bìa: Giới thiệu chuyên đề so sánh Airflow vs Dagster trên bài toán bóc tách PDF thực chiến. Giải thích lý do chọn chủ đề và mục tiêu chuyển dịch On-Premise.")

    # =========================================================================
    # SLIDE 2: AWS STEP FUNCTION
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Hạ Tầng Cloud Hiện Tại", "AWS Step Functions & Thách Thức Chuyển Đổi",
               "Đánh giá hiện trạng hạ tầng Cloud hiện tại và động lực di chuyển On-Premise")

    col_w = Inches(5.65)
    col_gap = Inches(0.433)
    c1_x = Inches(0.8)
    c2_x = c1_x + col_w + col_gap
    cards_y = Inches(1.68)
    cards_h = Inches(5.3)

    # Pros Card
    card_pros = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c1_x, cards_y, col_w, cards_h)
    card_pros.fill.solid()
    card_pros.fill.fore_color.rgb = CARD_BG
    card_pros.line.color.rgb = ACCENT_GREEN
    card_pros.line.width = Pt(1.5)
    tf = card_pros.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.28)
    tf.margin_right = Inches(0.28)
    tf.margin_top = Inches(0.24)
    tf.margin_bottom = Inches(0.2)

    p = tf.paragraphs[0]
    p.text = "✅ LỢI THẾ HIỆN TẠI (PROS)"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    for title, desc in [
        ("Hoàn toàn Serverless:", "Không tốn công vận hành hạ tầng máy chủ hay cụm cluster."),
        ("Auto-Scaling tự động:", "Tự động scale theo tải khi có hàng nghìn request đổ về."),
        ("Pay-as-you-go:", "Chỉ trả phí dựa trên số lượng request và chuyển trạng thái thực tế."),
        ("Tích hợp sâu hệ sinh thái AWS:", "Kết nối trực tiếp Lambda, S3, DynamoDB, SQS mượt mà.")
    ]:
        pt = tf.add_paragraph()
        pt.text = f"• {title}"
        pt.font.name = FONT_MAIN
        pt.font.bold = True
        pt.font.size = Pt(12)
        pt.font.color.rgb = TEXT_MAIN
        pt.space_before = Pt(11)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = FONT_MAIN
        pd.font.size = Pt(10.5)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_before = Pt(2)

    # Cons Card
    card_cons = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c2_x, cards_y, col_w, cards_h)
    card_cons.fill.solid()
    card_cons.fill.fore_color.rgb = CARD_BG
    card_cons.line.color.rgb = ACCENT_ROSE
    card_cons.line.width = Pt(1.5)
    tf = card_cons.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.28)
    tf.margin_right = Inches(0.28)
    tf.margin_top = Inches(0.24)
    tf.margin_bottom = Inches(0.2)

    p = tf.paragraphs[0]
    p.text = "❌ HẠN CHẾ & RỦI RO (CONS)"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ROSE

    for title, desc in [
        ("Khó khăn khi Test & Debug Local:", "Mô phỏng Step Function ở local rất phức tạp, chu kỳ phản hồi phát triển chậm."),
        ("Chi phí tăng vọt khi Scale tải lớn:", "Chi phí state transition rất đắt đỏ khi xử lý hàng triệu hóa đơn/tháng."),
        ("Rủi ro Vendor Lock-in:", "Bị ràng buộc mã nguồn vào dịch vụ AWS, khó chuyển sang Cloud khác."),
        ("Tuân thủ On-Premise & Bảo mật:", "Khách hàng tài chính/ngân hàng yêu cầu dữ liệu nhạy cảm phải xử lý nội bộ.")
    ]:
        pt = tf.add_paragraph()
        pt.text = f"• {title}"
        pt.font.name = FONT_MAIN
        pt.font.bold = True
        pt.font.size = Pt(12)
        pt.font.color.rgb = TEXT_MAIN
        pt.space_before = Pt(11)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = FONT_MAIN
        pd.font.size = Pt(10.5)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_before = Pt(2)

    add_speaker_notes(s2, "Speaker Note: Nêu rõ bối cảnh các dự án trước đây dùng AWS Step Functions. Đặt câu hỏi chiến lược: Khi khách hàng yêu cầu On-Premise để bảo mật dữ liệu và tiết kiệm chi phí lâu dài, ta sẽ chọn công cụ nào?")

    # =========================================================================
    # SLIDE 3: BÀI TOÁN HÓA ĐƠN & SƠ ĐỒ FLOWCHART
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Bài Toán Nghiệp Vụ", "Bài Toán Tự Động Bóc Tách & Duyệt Hóa Đơn",
               "Nghiệp vụ 4 loại hóa đơn & Luồng kiểm toán tài chính (PDF -> Data)")

    # Left Column: Business Specs Card
    card_left = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.68), Inches(5.2), Inches(5.3))
    card_left.fill.solid()
    card_left.fill.fore_color.rgb = CARD_BG
    card_left.line.color.rgb = BORDER_CYAN
    card_left.line.width = Pt(1.5)
    tf = card_left.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.24)
    tf.margin_right = Inches(0.24)
    tf.margin_top = Inches(0.22)
    tf.margin_bottom = Inches(0.18)

    p = tf.paragraphs[0]
    p.text = "📋 QUY TRÌNH NGHIỆP VỤ & KIỂM TOÁN"
    p.font.name = FONT_MAIN
    p.font.size = Pt(14.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    specs = [
        ("1. Phân loại 4 trang hóa đơn (4 Types):", [
            "Trang 1 (VAT): Lấy MST, Tiền hàng, Tiền thuế GTGT 10%.",
            "Trang 2 (Utility): Lấy Customer ID đối chiếu tiền điện/nước.",
            "Trang 3 (Travel): Lấy Employee ID để hoàn ứng công tác.",
            "Trang 4 (Retail): ⚠️ Gắn cờ cảnh báo: Không duyệt khấu trừ thuế!"
        ]),
        ("2. Tiêu chuẩn kiểm toán (Validation Rules):", [
            "Số học: Tiền hàng + Tiền thuế có khớp Tổng tiền không?",
            "Hạn mức: Tổng tiền toàn bộ hóa đơn có vượt 100M VNĐ không?"
        ]),
        ("3. Kết quả phê duyệt (Approval):", [
            "✅ Đạt chuẩn: Duyệt & Lưu vào Database / Ledger.",
            "❌ Lỗi / Vượt hạn mức: Dừng ngay lập tức (Hard Stop)!"
        ])
    ]

    for sec_title, sec_bullets in specs:
        pt = tf.add_paragraph()
        pt.text = sec_title
        pt.font.name = FONT_MAIN
        pt.font.bold = True
        pt.font.size = Pt(11.5)
        pt.font.color.rgb = TEXT_MAIN
        pt.space_before = Pt(8)

        for b in sec_bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.name = FONT_MAIN
            pb.font.size = Pt(9.8)
            pb.font.color.rgb = TEXT_MUTED
            pb.space_before = Pt(2)

    # Right Column: Flowchart Card
    fc_left = Inches(6.25)
    fc_w = Inches(6.283)
    fc_bg = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, fc_left, Inches(1.68), fc_w, Inches(5.3))
    fc_bg.fill.solid()
    fc_bg.fill.fore_color.rgb = RGBColor(12, 10, 24)
    fc_bg.line.color.rgb = BORDER_PURPLE
    fc_bg.line.width = Pt(1.5)

    fc_axis = fc_left + (fc_w / 2)

    # Node 1: Input PDF (Modern Flat Rounded Pill)
    n1_w = Inches(3.8)
    add_node_card(s3, fc_axis - (n1_w / 2), Inches(1.88), n1_w, Inches(0.44),
                  "📄 Input PDF (4 Pages)", "",
                  bg_color=RGBColor(241, 245, 249), border_color=RGBColor(148, 163, 184),
                  title_color=RGBColor(15, 23, 42), title_size=11)

    add_arrow_down(s3, fc_axis - Inches(0.2), Inches(2.34), text="↓", color=RGBColor(148, 163, 184))

    # Node 2: Split Pages
    add_node_card(s3, fc_axis - (n1_w / 2), Inches(2.62), n1_w, Inches(0.44),
                  "✂️ Split Pages", "",
                  bg_color=RGBColor(241, 245, 249), border_color=RGBColor(148, 163, 184),
                  title_color=RGBColor(15, 23, 42), title_size=11)

    add_arrow_down(s3, fc_axis - Inches(0.2), Inches(3.08), text="↓", color=RGBColor(148, 163, 184))

    # Parallel 4 Branches
    branch_w = Inches(1.38)
    branch_gap = Inches(0.1)
    branches_total = (branch_w * 4) + (branch_gap * 3)
    bx_start = fc_axis - (branches_total / 2)
    by = Inches(3.36)
    bh = Inches(0.95)

    add_node_card(s3, bx_start, by, branch_w, bh,
                  "VAT Invoice –", "Tax ID, Net & VAT",
                  bg_color=RGBColor(248, 250, 252), border_color=ACCENT_CYAN,
                  title_color=RGBColor(2, 132, 199), sub_color=RGBColor(15, 23, 42), title_size=9.5, sub_size=8.5)

    add_node_card(s3, bx_start + (branch_w + branch_gap), by, branch_w, bh,
                  "Utility Invoice –", "Customer ID",
                  bg_color=RGBColor(248, 250, 252), border_color=ACCENT_CYAN,
                  title_color=RGBColor(2, 132, 199), sub_color=RGBColor(15, 23, 42), title_size=9.5, sub_size=8.5)

    add_node_card(s3, bx_start + (branch_w + branch_gap)*2, by, branch_w, bh,
                  "Travel Expense –", "Employee ID",
                  bg_color=RGBColor(248, 250, 252), border_color=ACCENT_CYAN,
                  title_color=RGBColor(2, 132, 199), sub_color=RGBColor(15, 23, 42), title_size=9.5, sub_size=8.5)

    add_node_card(s3, bx_start + (branch_w + branch_gap)*3, by, branch_w, bh,
                  "Retail Receipt –", "⚠️ Reject Tax Deduct",
                  bg_color=RGBColor(255, 241, 242), border_color=ACCENT_ROSE,
                  title_color=RGBColor(190, 18, 60), sub_color=RGBColor(153, 27, 27), title_size=9.5, sub_size=8.5)

    add_arrow_down(s3, fc_axis - Inches(0.2), Inches(4.33), text="↓", color=RGBColor(148, 163, 184))

    # Node 3: Validation Box
    n3_w = Inches(5.5)
    add_node_card(s3, fc_axis - (n3_w / 2), Inches(4.62), n3_w, Inches(0.72),
                  "🔍 VALIDATION –",
                  "Math check: Net + VAT = Total?   |   Within budget: <= 100M VND?",
                  bg_color=RGBColor(254, 243, 199), border_color=ACCENT_AMBER,
                  title_color=RGBColor(120, 53, 15), sub_color=RGBColor(146, 64, 14),
                  title_size=11, sub_size=9.5, bold_title=True)

    add_arrow_down(s3, fc_axis - Inches(0.2), Inches(5.36), text="↓", color=RGBColor(148, 163, 184))

    # 2 Result Boxes: Pass & Fail
    res_w = Inches(2.65)
    res_gap = Inches(0.35)
    res_start = fc_axis - (res_w * 2 + res_gap) / 2
    add_node_card(s3, res_start, Inches(5.64), res_w, Inches(0.98),
                  "✅ APPROVED (Pass)", "Write to Database / Ledger",
                  bg_color=RGBColor(220, 252, 231), border_color=ACCENT_GREEN,
                  title_color=RGBColor(20, 83, 45), sub_color=RGBColor(22, 101, 52),
                  title_size=11, sub_size=9.5, bold_title=True)

    add_node_card(s3, res_start + res_w + res_gap, Inches(5.64), res_w, Inches(0.98),
                  "❌ REJECTED (Fail)", "Hard Stop Pipeline!",
                  bg_color=RGBColor(254, 226, 226), border_color=ACCENT_ROSE,
                  title_color=RGBColor(153, 27, 27), sub_color=RGBColor(127, 29, 29),
                  title_size=11, sub_size=9.5, bold_title=True)

    add_speaker_notes(s3, "Speaker Note: Giới thiệu bài toán nghiệp vụ bóc tách 4 trang hóa đơn và luồng kiểm toán tài chính. Chỉ rõ sơ đồ dòng chảy từ tiếp nhận đến duyệt hoặc dừng khẩn cấp.")

    # =========================================================================
    # SLIDE 4: GÓC NHÌN AIRFLOW & DAGSTER (ALL SLEEK ROUNDED CARDS, ZERO CANS!)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "Triết Lý Cốt Lõi", "Đối Chiếu Kiến Trúc: Task-Centric vs Asset-Centric",
               "Chuỗi hành động thực thi (Airflow Tasks) vs Mạng lưới tài sản dữ liệu (Dagster Assets)")

    half_w = Inches(5.65)
    gap_half = Inches(0.433)
    left_af_x = Inches(0.8)
    right_dg_x = left_af_x + half_w + gap_half
    af_axis = left_af_x + (half_w / 2)
    dg_axis = right_dg_x + (half_w / 2)

    # Left Container: Airflow Diagram Card
    box_af_card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_af_x, Inches(1.68), half_w, Inches(5.3))
    box_af_card.fill.solid()
    box_af_card.fill.fore_color.rgb = CARD_BG
    box_af_card.line.color.rgb = ACCENT_CYAN
    box_af_card.line.width = Pt(1.5)

    # Airflow Card Header Bar matching slides copy.html
    h_af_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_af_x + Inches(0.12), Inches(1.76), half_w - Inches(0.24), Inches(0.32))
    h_af_box.fill.solid()
    h_af_box.fill.fore_color.rgb = RGBColor(12, 28, 48)
    h_af_box.line.color.rgb = RGBColor(56, 189, 248)
    h_af_box.line.width = Pt(1)
    tf_haf = h_af_box.text_frame
    tf_haf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf_haf.paragraphs[0]
    p.text = "⚙️ GÓC NHÌN AIRFLOW (Task-Centric)  |  Làm gì tiếp? • Mù dữ liệu • XCom qua DB"
    p.font.name = FONT_MAIN
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.alignment = PP_ALIGN.CENTER

    # Airflow Nodes
    node_af_w = Inches(4.7)
    add_node_card(s4, af_axis - (node_af_w / 2), Inches(2.16), node_af_w, Inches(0.42),
                  "📄 ingest_multipage_invoice_pdf", "Input: 4-Page PDF",
                  bg_color=CARD_BG_ALT, border_color=ACCENT_CYAN, title_size=10, sub_size=8.5)

    add_arrow_down(s4, af_axis - Inches(0.2), Inches(2.58), text="↓", color=ACCENT_CYAN)

    add_node_card(s4, af_axis - (node_af_w / 2), Inches(2.82), node_af_w, Inches(0.42),
                  "⚙️ check_pdf_integrity", "@task.branch",
                  bg_color=CARD_BG_ALT, border_color=ACCENT_AMBER, title_color=ACCENT_AMBER, title_size=10, sub_size=8.5)

    add_arrow_label(s4, af_axis, Inches(3.24), "↓ Valid File", color=ACCENT_PURPLE, w=Inches(2.0))

    add_node_card(s4, af_axis - (node_af_w / 2), Inches(3.48), node_af_w, Inches(0.42),
                  "✂️ classify_invoice_pages", "Group 4 Types",
                  bg_color=CARD_BG_ALT, border_color=BORDER_PURPLE, title_size=10, sub_size=8.5)

    add_arrow_down(s4, af_axis - Inches(0.2), Inches(3.90), text="↓", color=ACCENT_CYAN)

    # 4 Parallel Task Boxes
    af_bw = Inches(1.15)
    af_bgap = Inches(0.08)
    af_total_w = (af_bw * 4) + (af_bgap * 3)
    af_bx_start = af_axis - (af_total_w / 2)
    af_by = Inches(4.14)
    af_bh = Inches(0.68)

    add_node_card(s4, af_bx_start, af_by, af_bw, af_bh,
                  "⚡ VAT", "Cloud: 55M",
                  bg_color=CARD_BG_ALT, border_color=ACCENT_CYAN, title_color=ACCENT_CYAN, title_size=9, sub_size=8)
    add_node_card(s4, af_bx_start + (af_bw + af_bgap), af_by, af_bw, af_bh,
                  "⚡ Utility", "EVN: 1.85M",
                  bg_color=CARD_BG_ALT, border_color=ACCENT_CYAN, title_color=ACCENT_CYAN, title_size=9, sub_size=8)
    add_node_card(s4, af_bx_start + (af_bw + af_bgap)*2, af_by, af_bw, af_bh,
                  "⚡ Travel", "Flight: 3.2M",
                  bg_color=CARD_BG_ALT, border_color=ACCENT_CYAN, title_color=ACCENT_CYAN, title_size=9, sub_size=8)
    add_node_card(s4, af_bx_start + (af_bw + af_bgap)*3, af_by, af_bw, af_bh,
                  "⚡ Retail (⚠️)", "Retail: 150K",
                  bg_color=RGBColor(255, 241, 242), border_color=ACCENT_ROSE, title_color=RGBColor(153, 27, 27),
                  sub_color=RGBColor(153, 27, 27), title_size=8.5, sub_size=7.5)

    add_arrow_down(s4, af_axis - Inches(0.2), Inches(4.84), text="↓", color=ACCENT_CYAN)

    # T4 Collect
    add_node_card(s4, af_axis - (node_af_w / 2), Inches(5.08), node_af_w, Inches(0.42),
                  "📥 collect_extracted_invoices", "TriggerRule: NONE_FAILED_MIN_ONE_SUCCESS",
                  bg_color=CARD_BG_ALT, border_color=BORDER_PURPLE, title_size=9.5, sub_size=8)

    add_arrow_down(s4, af_axis - Inches(0.2), Inches(5.50), text="↓", color=ACCENT_CYAN)

    # T5 Outcomes
    res_af_w = Inches(2.32)
    res_af_gap = Inches(0.18)
    res_af_start = af_axis - (res_af_w * 2 + res_af_gap) / 2
    add_node_card(s4, res_af_start, Inches(5.74), res_af_w, Inches(0.68),
                  "✅ lock_publish_ledger", "Pass <= 100M: 60.2M",
                  bg_color=ACCENT_GREEN_BG, border_color=ACCENT_GREEN, title_color=RGBColor(74, 222, 128),
                  sub_color=TEXT_MAIN, title_size=9.5, sub_size=8)

    add_node_card(s4, res_af_start + res_af_w + res_af_gap, Inches(5.74), res_af_w, Inches(0.68),
                  "❌ alert_audit_violation", "Fail > 100M: Skip Ledger",
                  bg_color=ACCENT_ROSE_BG, border_color=ACCENT_ROSE, title_color=RGBColor(248, 113, 113),
                  sub_color=TEXT_MAIN, title_size=9.5, sub_size=8)

    # Right Container: Dagster Diagram Card
    box_dg_card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_dg_x, Inches(1.68), half_w, Inches(5.3))
    box_dg_card.fill.solid()
    box_dg_card.fill.fore_color.rgb = CARD_BG
    box_dg_card.line.color.rgb = ACCENT_PURPLE
    box_dg_card.line.width = Pt(1.5)

    # Dagster Card Header Bar matching slides copy.html
    h_dg_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_dg_x + Inches(0.12), Inches(1.76), half_w - Inches(0.24), Inches(0.32))
    h_dg_box.fill.solid()
    h_dg_box.fill.fore_color.rgb = RGBColor(32, 14, 52)
    h_dg_box.line.color.rgb = RGBColor(192, 132, 252)
    h_dg_box.line.width = Pt(1)
    tf_hdg = h_dg_box.text_frame
    tf_hdg.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf_hdg.paragraphs[0]
    p.text = "💎 GÓC NHÌN DAGSTER (Asset-Centric)  |  Tạo tài sản gì? • Khiên Checks • I/O Manager"
    p.font.name = FONT_MAIN
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.alignment = PP_ALIGN.CENTER

    # Dagster Assets (REPLACED ALL UGLY CANS WITH SLEEK INDIGO/PURPLE ROUNDED CARDS!)
    node_dg_w = Inches(4.8)
    add_node_card(s4, dg_axis - (node_dg_w / 2), Inches(2.16), node_dg_w, Inches(0.42),
                  "📄 raw_multipage_invoice_pdf", "🛡️ check_pdf_file_integrity",
                  bg_color=DG_INDIGO, border_color=DG_INDIGO_BORDER,
                  title_color=RGBColor(224, 231, 255), sub_color=ACCENT_CYAN, title_size=10, sub_size=8.5)

    add_arrow_down(s4, dg_axis - Inches(0.2), Inches(2.58), text="↓", color=ACCENT_PURPLE)

    add_node_card(s4, dg_axis - (node_dg_w / 2), Inches(2.82), node_dg_w, Inches(0.42),
                  "📑 extracted_invoice_pages", "OCR & AI Parsing",
                  bg_color=DG_INDIGO, border_color=DG_INDIGO_BORDER,
                  title_color=RGBColor(224, 231, 255), sub_color=TEXT_MUTED, title_size=10, sub_size=8.5)

    add_arrow_down(s4, dg_axis - Inches(0.2), Inches(3.24), text="↓", color=ACCENT_PURPLE)

    # 4 Parallel Assets - Sleek Deep Purple Tech Cards (NO CANS!)
    dg_bw = Inches(1.15)
    dg_bgap = Inches(0.08)
    dg_total_w = (dg_bw * 4) + (dg_bgap * 3)
    dg_bx_start = dg_axis - (dg_total_w / 2)
    dg_by = Inches(3.48)
    dg_bh = Inches(0.70)

    add_node_card(s4, dg_bx_start, dg_by, dg_bw, dg_bh,
                  "⚡ vat_invoices", "55M (VAT 5M)",
                  bg_color=DG_PURPLE_DEEP, border_color=DG_PURPLE_BORDER,
                  title_color=RGBColor(243, 232, 255), title_size=8.5, sub_size=8)
    add_node_card(s4, dg_bx_start + (dg_bw + dg_bgap), dg_by, dg_bw, dg_bh,
                  "⚡ utility_inv", "EVN: 1.85M",
                  bg_color=DG_PURPLE_DEEP, border_color=DG_PURPLE_BORDER,
                  title_color=RGBColor(243, 232, 255), title_size=8.5, sub_size=8)
    add_node_card(s4, dg_bx_start + (dg_bw + dg_bgap)*2, dg_by, dg_bw, dg_bh,
                  "⚡ reimburse", "Flight: 3.2M",
                  bg_color=DG_PURPLE_DEEP, border_color=DG_PURPLE_BORDER,
                  title_color=RGBColor(243, 232, 255), title_size=8.5, sub_size=8)
    add_node_card(s4, dg_bx_start + (dg_bw + dg_bgap)*3, dg_by, dg_bw, dg_bh,
                  "⚡ invalid_inv", "Retail: 150K ⚠️",
                  bg_color=DG_ROSE_DEEP, border_color=ACCENT_ROSE,
                  title_color=RGBColor(254, 205, 211), title_size=8.5, sub_size=8)

    add_arrow_label(s4, dg_axis, Inches(4.20), "↓ Fan-In Convergence", color=ACCENT_PURPLE, w=Inches(2.6))

    # A3 Categorized Invoices with 2 Shields (SLEEK ROUNDED CARD!)
    add_node_card(s4, dg_axis - (node_dg_w / 2), Inches(4.48), node_dg_w, Inches(0.55),
                  "📊 categorized_invoices",
                  "🛡️ check_vat_tax_math  |  🛡️ check_budget_limit (blocking=True)",
                  bg_color=DG_PURPLE_DEEP, border_color=DG_PURPLE_BORDER,
                  title_color=RGBColor(243, 232, 255), sub_color=ACCENT_AMBER, title_size=10, sub_size=8.5)

    add_arrow_label(s4, dg_axis, Inches(5.06), "↓ Materialize", color=ACCENT_GREEN, w=Inches(2.0))

    # A4 Ledger Asset (SLEEK RICH FOREST GREEN ROUNDED CARD!)
    add_node_card(s4, dg_axis - (node_dg_w / 2), Inches(5.32), node_dg_w, Inches(0.60),
                  "💎 monthly_expense_ledger",
                  "Approved: 60.2M VND (Published to Storage & Dashboard)",
                  bg_color=ACCENT_GREEN_BG, border_color=ACCENT_GREEN,
                  title_color=RGBColor(74, 222, 128), sub_color=TEXT_MAIN, title_size=10.5, sub_size=8.5)

    add_speaker_notes(s4, "Speaker Note: Phân tích sự khác biệt sâu sắc giữa 2 sơ đồ: Airflow quản lý chuỗi task hình chữ nhật và phải tự viết nhánh rẽ; Dagster quản lý chuỗi tài sản dữ liệu sống đi kèm các chiếc khiên kiểm định Asset Checks bảo vệ chất lượng dữ liệu.")

    # =========================================================================
    # SLIDE 5: 1 TASK TRONG AIRFLOW (ALL SLEEK ROUNDED CARDS, ZERO CANS!)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Deep Dive Airflow", "Vòng Đời Thực Thi 1 Task Trong Apache Airflow",
               "Chu trình thực thi 6 bước & Các điểm nghẽn kiến trúc (DAG Parsing Loop, DB Hits, XCom DB)")

    af_step_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.68), Inches(6.4), Inches(5.3))
    af_step_card.fill.solid()
    af_step_card.fill.fore_color.rgb = CARD_BG
    af_step_card.line.color.rgb = ACCENT_CYAN
    af_step_card.line.width = Pt(1.5)

    t_af_step = s5.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(6.0), Inches(0.32))
    tf = t_af_step.text_frame
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = "⚙️ AIRFLOW TASK EXECUTION (Chu Trình 6 Bước)"
    p.font.name = FONT_MAIN
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    # All rounded rectangle steps (NO CANS!)
    af_steps = [
        ("📁 1. Write Code File", "(dags/invoice_dag.py)",
         RGBColor(30, 27, 75), RGBColor(129, 140, 248)),
        ("🔄 2. DAG Parsing Loop (Mỗi 30 Giây)", "(Scheduler re-compiles Python from disk - CPU Overhead)",
         ACCENT_ROSE_BG, ACCENT_ROSE),
        ("🗄️ 3. Task State Transitions (DB Hits)", "[NONE] ➔ [SCHEDULED] ➔ [QUEUED] ➔ UPDATE task_instance",
         ACCENT_ROSE_BG, ACCENT_ROSE),
        ("⚡ 4. Worker Pulls & Runs Task", "(State: [RUNNING] trên Celery Worker / K8s Pod)",
         CARD_BG_ALT, ACCENT_CYAN),
        ("📦 5. Data Exchange via XCom DB", "INSERT INTO xcom VALUES (...) (JSON/Pickle Payloads in Postgres)",
         ACCENT_ROSE_BG, ACCENT_ROSE),
        ("💻 6. Webserver DB Polling", "SELECT state ➔ Tô màu ô Xanh/Đỏ (⚠️ MÙ DỮ LIỆU)",
         CARD_BG_ALT, ACCENT_AMBER),
    ]

    sy = Inches(2.14)
    step_w = Inches(5.9)
    step_h = Inches(0.48)
    step_gap = Inches(0.28)
    af_axis_5 = Inches(0.8) + (Inches(6.4) / 2)

    for idx, (title, sub, bg, bcol) in enumerate(af_steps):
        add_node_card(s5, af_axis_5 - (step_w / 2), sy, step_w, step_h,
                      title, sub, bg_color=bg, border_color=bcol, title_size=10, sub_size=8)
        if idx < len(af_steps) - 1:
            add_arrow_down(s5, af_axis_5 - Inches(0.2), sy + step_h + Inches(0.02), text="↓", color=ACCENT_CYAN)
        sy += (step_h + step_gap)

    # Right Container: 4 Step-by-Step Analysis Cards
    rx = Inches(7.55)
    rw = Inches(4.983)
    ry = Inches(1.68)
    rh = Inches(1.20)
    rgap = Inches(0.16)

    af_cards_data = [
        ("🔄 1. Bị Ép Re-Parse Liên Tục (30s/lần)", ACCENT_AMBER,
         "Scheduler không lưu cấu trúc trên RAM mà liên tục đọc và biên dịch lại code Python. Lỡ import OCR nặng ngoài hàm ➔ Treo 100% CPU toàn cụm."),
        ("🗄️ 2. State Machine Bắn Query DB Dồn Dập", ACCENT_ROSE,
         "Mỗi bước chuyển trạng thái (None ➔ Scheduled ➔ Queued ➔ Running ➔ Success) đều UPDATE Postgres ➔ Nguy cơ lock bảng khi tải lớn."),
        ("📦 3. Ép Nạp Dữ Liệu XCom Thẳng Vào Postgres", BORDER_PURPLE,
         "Khi task return, Airflow serialize rồi INSERT INTO xcom. Dữ liệu lớn (ảnh hóa đơn, DataFrame) làm phình to DB và nghẽn I/O hệ thống."),
        ("👁️ 4. Kết Thúc Bằng 'Mù Dữ Liệu' Trên UI", ACCENT_ROSE,
         "Webserver chỉ đọc DB để tô màu ô vuông Xanh/Đỏ. Kỹ sư hoàn toàn không biết bên trong có bao nhiêu tiền, bao nhiêu hóa đơn nếu không mò log.")
    ]

    for idx, (ctitle, ccolor, cdesc) in enumerate(af_cards_data):
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, rx, ry + (rh + rgap)*idx, rw, rh)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG_ALT
        card.line.color.rgb = ccolor
        card.line.width = Pt(1.2)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.12)
        tf.margin_bottom = Inches(0.1)

        p = tf.paragraphs[0]
        p.text = ctitle
        p.font.name = FONT_MAIN
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = ccolor

        pd = tf.add_paragraph()
        pd.text = cdesc
        pd.font.name = FONT_MAIN
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_before = Pt(4)

    add_speaker_notes(s5, "Speaker Note: Mổ xẻ 6 bước thực thi trong 1 task Airflow và 4 điểm nghẽn: CPU parsing loop, database lock do state machine, xcom phình to DB và UI bị mù dữ liệu.")

    # =========================================================================
    # SLIDE 6: TRONG DAGSTER (ALL SLEEK ROUNDED CARDS, ZERO CANS!)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Deep Dive Dagster", "Kiến Trúc Điều Phối Hiện Đại Trong Dagster",
               "Chu trình phân tách 6 bước (gRPC Code Server, Ephemeral Worker, I/O Manager, Khiên Asset Checks)")

    dg_step_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.68), Inches(6.4), Inches(5.3))
    dg_step_card.fill.solid()
    dg_step_card.fill.fore_color.rgb = CARD_BG
    dg_step_card.line.color.rgb = ACCENT_PURPLE
    dg_step_card.line.width = Pt(1.5)

    t_dg_step = s6.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(6.0), Inches(0.32))
    tf = t_dg_step.text_frame
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = "💎 DAGSTER ASSET MATERIALIZATION (Chu Trình Phân Tách)"
    p.font.name = FONT_MAIN
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE

    # All rounded rectangle steps (NO CANS!)
    dg_steps = [
        ("📦 1. User Code Server (Isolated Process)", "assets.py với các hàm pure Python trong môi trường độc lập",
         RGBColor(30, 27, 75), RGBColor(129, 140, 248)),
        ("🌐 2. gRPC Discovery (Zero Scheduler Load)", "Gửi Asset Schema & Lineage qua gRPC - Không bao giờ parse định kỳ",
         CARD_BG_ALT, ACCENT_PURPLE),
        ("⏱️ 3. Trigger & Run Execution Plan", "Sensor / Schedule / UI Materialize ➔ Bắn Event log vào DB",
         CARD_BG_ALT, ACCENT_CYAN),
        ("🚀 4. Launch Ephemeral Worker", "Khởi động Pod/Container độc lập để thực thi tính toán Asset",
         CARD_BG_ALT, ACCENT_PURPLE),
        ("💾 5A. I/O Manager  &  🛡️ 5B. Asset Checks", "Payloads đẩy thẳng S3/MinIO  |  @asset_check(blocking=True) kiểm toán tại chỗ",
         ACCENT_GREEN_BG, ACCENT_GREEN),
        ("📊 6. Real-time Event Log & UI Lineage", "Hiện giá trị tiền, số lượng hóa đơn trực quan ngay trên Dashboard",
         RGBColor(46, 16, 101), ACCENT_PURPLE),
    ]

    sy = Inches(2.14)
    dg_axis_6 = Inches(0.8) + (Inches(6.4) / 2)

    for idx, (title, sub, bg, bcol) in enumerate(dg_steps):
        add_node_card(s6, dg_axis_6 - (step_w / 2), sy, step_w, step_h,
                      title, sub, bg_color=bg, border_color=bcol, title_size=10, sub_size=8)
        if idx < len(dg_steps) - 1:
            add_arrow_down(s6, dg_axis_6 - Inches(0.2), sy + step_h + Inches(0.02), text="↓", color=ACCENT_PURPLE)
        sy += (step_h + step_gap)

    # Right Container: 4 Step-by-Step Analysis Cards
    dg_cards_data = [
        ("🛡️ 1. Khám Phá Metadata Qua gRPC (Zero Load)", RGBColor(129, 140, 248),
         "Code người dùng chạy trong tiến trình riêng. Nền tảng chỉ dùng gRPC để hỏi schema và lineage, hoàn toàn không nạp code Python của user vào Scheduler."),
        ("🚀 2. Chạy Trong Worker Độc Lập (Ephemeral)", ACCENT_PURPLE,
         "Mỗi lần chạy bật một container/pod độc lập thực thi hàm Asset thuần khiết. Code có crash hay OOM thì Daemon và Webserver vẫn an toàn 100%."),
        ("💾 3. I/O Manager Độc Lập & Không Đụng DB", ACCENT_GREEN,
         "Dữ liệu trả về được I/O Manager tự động đẩy thẳng lên S3/MinIO hoặc Snowflake. Database hệ thống chỉ lưu nhật ký sự kiện, không lo phình bộ nhớ."),
        ("🛡️ 4. Asset Checks Đánh Chặn & Báo Cáo Trên UI", ACCENT_CYAN,
         "Kiểm định chất lượng dữ liệu được gắn trực tiếp vào Asset. Nếu vi phạm trần 100M sẽ chặn downstream ngay và cảnh báo trên giao diện.")
    ]

    for idx, (ctitle, ccolor, cdesc) in enumerate(dg_cards_data):
        card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, rx, ry + (rh + rgap)*idx, rw, rh)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG_ALT
        card.line.color.rgb = ccolor
        card.line.width = Pt(1.2)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.12)
        tf.margin_bottom = Inches(0.1)

        p = tf.paragraphs[0]
        p.text = ctitle
        p.font.name = FONT_MAIN
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = ccolor

        pd = tf.add_paragraph()
        pd.text = cdesc
        pd.font.name = FONT_MAIN
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_before = Pt(4)

    add_speaker_notes(s6, "Speaker Note: Giới thiệu 4 ưu điểm vượt trội trong kiến trúc Dagster: gRPC code server cách ly mã nguồn, ephemeral worker tự dọn dẹp, I/O manager tách biệt storage và Asset Checks bảo vệ dữ liệu.")

    # =========================================================================
    # SLIDE 7: HẠ TẦNG ON-PREMISE & CI/CD
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Triển Khai & Vận Hành", "Hạ Tầng On-Premise & Năng Lực Kiểm Thử CI/CD",
               "Kiến trúc cụm On-Prem (Kubernetes, MinIO, PostgreSQL) và Tốc độ kiểm thử tự động")

    c_infra = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c1_x, cards_y, col_w, cards_h)
    c_infra.fill.solid()
    c_infra.fill.fore_color.rgb = CARD_BG
    c_infra.line.color.rgb = ACCENT_CYAN
    c_infra.line.width = Pt(1.5)
    tf = c_infra.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.28)
    tf.margin_right = Inches(0.28)
    tf.margin_top = Inches(0.24)
    tf.margin_bottom = Inches(0.2)

    p = tf.paragraphs[0]
    p.text = "🏢 HẠ TẦNG ON-PREMISE (K8S & STORAGE)"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    for t_i, d_i in [
        ("Kubernetes Cluster:", "Triển khai điều phối bằng Helm Charts chính thức của Airflow / Dagster."),
        ("MinIO (Object Storage S3-Compatible):", "Thay thế hoàn hảo AWS S3 để lưu trữ file PDF hóa đơn và artifacts."),
        ("PostgreSQL HA:", "Lưu trữ metadata của hệ thống với cụm replica độ tin cậy cao."),
        ("Vault & Keycloak:", "Quản lý secret và xác thực bảo mật tập trung cho toàn bộ dịch vụ.")
    ]:
        pt = tf.add_paragraph()
        pt.text = f"• {t_i}"
        pt.font.name = FONT_MAIN
        pt.font.bold = True
        pt.font.size = Pt(12)
        pt.font.color.rgb = TEXT_MAIN
        pt.space_before = Pt(11)

        pd = tf.add_paragraph()
        pd.text = d_i
        pd.font.name = FONT_MAIN
        pd.font.size = Pt(10.5)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_before = Pt(2)

    # Right: CI/CD Testing Comparison
    c_test = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c2_x, cards_y, col_w, cards_h)
    c_test.fill.solid()
    c_test.fill.fore_color.rgb = CARD_BG
    c_test.line.color.rgb = ACCENT_GREEN
    c_test.line.width = Pt(1.5)
    tf = c_test.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.28)
    tf.margin_right = Inches(0.28)
    tf.margin_top = Inches(0.24)
    tf.margin_bottom = Inches(0.2)

    p = tf.paragraphs[0]
    p.text = "⚡ TỐC ĐỘ KIỂM THỬ CI/CD & DEVELOPER UX"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    for t_i, d_i in [
        ("Airflow Unit Test (Phức tạp, 5-15 giây):", "Cần khởi tạo SQLite database giả lập, mock context và task instance. Chạy chậm trong CI."),
        ("Dagster In-Memory Test (Cực nhanh, ~0.12 giây):", "Hỗ trợ materialize([asset_name]) trực tiếp trong RAM, không cần database hay server. Tích hợp trơn tru vào Pytest."),
        ("Tự tin Refactor:", "Kỹ sư tự do thay đổi logic xử lý hóa đơn và kiểm tra ngay lập tức tại máy cá nhân."),
        ("Tối ưu chu kỳ phản hồi:", "Rút ngắn thời gian phát hiện lỗi từ hàng phút xuống chỉ vài trăm mili-giây.")
    ]:
        pt = tf.add_paragraph()
        pt.text = f"• {t_i}"
        pt.font.name = FONT_MAIN
        pt.font.bold = True
        pt.font.size = Pt(12)
        pt.font.color.rgb = TEXT_MAIN
        pt.space_before = Pt(11)

        pd = tf.add_paragraph()
        pd.text = d_i
        pd.font.name = FONT_MAIN
        pd.font.size = Pt(10.5)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_before = Pt(2)

    add_speaker_notes(s7, "Speaker Note: Giới thiệu mô hình hạ tầng On-Premise chuẩn doanh nghiệp và so sánh trải nghiệm developer: Dagster vượt trội nhờ khả năng test in-memory 0.12s.")

    # =========================================================================
    # SLIDE 8: MA TRẬN SO SÁNH KỸ THUẬT (TABLE)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Bảng Điểm Kỹ Thuật", "Ma Trận So Sánh Kỹ Thuật Tổng Hợp",
               "Đánh giá 7 tiêu chí so sánh toàn diện giữa Apache Airflow và Dagster")

    rows, cols = 8, 4
    table_left = Inches(0.8)
    table_top = Inches(1.72)
    table_w = Inches(11.733)
    table_h = Inches(5.2)
    table_shape = s8.shapes.add_table(rows, cols, table_left, table_top, table_w, table_h)
    table = table_shape.table
    table.columns[0].width = Inches(2.3)
    table.columns[1].width = Inches(4.25)
    table.columns[2].width = Inches(4.25)
    table.columns[3].width = Inches(0.933)

    headers = ["Tiêu Chí", "Apache Airflow", "Dagster", "Thắng"]
    for col_idx, h_text in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = Inches(0.12)
        cell.margin_right = Inches(0.12)
        cell.margin_top = Inches(0.06)
        cell.margin_bottom = Inches(0.06)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CARD_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_MAIN
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = ACCENT_CYAN if col_idx != 3 else ACCENT_AMBER
        p.alignment = PP_ALIGN.CENTER if col_idx == 3 else PP_ALIGN.LEFT

    matrix_data = [
        ("Mô hình cốt lõi", "Task-Centric (Workflow as Code)", "Asset-Centric (Data as Code)", "Dagster"),
        ("Quản lý Dữ liệu", "XCom qua Database (Dễ nghẽn)", "I/O Manager tự động (S3/MinIO)", "Dagster"),
        ("Kiểm định Dữ liệu", "Tự viết Task/Sensor kiểm tra", "Asset Checks 1st-class tích hợp", "Dagster"),
        ("Kiểm thử Local & CI", "Mock phức tạp, khởi tạo DB chậm", "In-Memory Test cực nhanh (0.12s)", "Dagster"),
        ("Độ chín & Cộng đồng", "10+ năm, tài liệu & provider khổng lồ", "Mới hơn, cộng đồng đang tăng trưởng", "Airflow"),
        ("Bảo mật & Phân quyền", "RBAC hoàn thiện, hỗ trợ LDAP/OAuth", "RBAC chủ yếu trên Dagster Cloud", "Airflow"),
        ("Điều phối Đa nhiệm", "Mạnh về Job hạ tầng / DevOps / Spark", "Mạnh về Modern Data Platform & AI/ML", "Hòa")
    ]

    for row_idx, data in enumerate(matrix_data, start=1):
        for col_idx, text in enumerate(data):
            cell = table.cell(row_idx, col_idx)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = Inches(0.12)
            cell.margin_right = Inches(0.12)
            cell.margin_top = Inches(0.05)
            cell.margin_bottom = Inches(0.05)
            cell.fill.solid()
            row_bg = CARD_BG if row_idx % 2 == 1 else RGBColor(14, 11, 26)
            cell.fill.fore_color.rgb = row_bg

            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.name = FONT_MAIN
            p.font.size = Pt(10.8)
            if col_idx == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_MAIN
            elif col_idx == 3:
                p.font.bold = True
                p.alignment = PP_ALIGN.CENTER
                if text == "Dagster":
                    p.font.color.rgb = ACCENT_PURPLE
                elif text == "Airflow":
                    p.font.color.rgb = ACCENT_CYAN
                else:
                    p.font.color.rgb = ACCENT_AMBER
            else:
                p.font.color.rgb = TEXT_MUTED

    add_speaker_notes(s8, "Speaker Note: Phân tích bảng so sánh 7 tiêu chí. Airflow vượt trội về độ phủ và hệ thống RBAC, trong khi Dagster vượt trội về quản trị dữ liệu, testing và kiến trúc.")

    # =========================================================================
    # SLIDE 9: KHI NÀO DÙNG AI? (CÂY QUYẾT ĐỊNH)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Định Vị Giải Pháp", "Định Vị Giải Pháp: Tiêu Chí Lựa Chọn Airflow vs Dagster",
               "Căn cứ lựa chọn công nghệ phù hợp với đặc thù dự án và bài toán của doanh nghiệp")

    box_when_af = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c1_x, cards_y, col_w, cards_h)
    box_when_af.fill.solid()
    box_when_af.fill.fore_color.rgb = CARD_BG
    box_when_af.line.color.rgb = ACCENT_CYAN
    box_when_af.line.width = Pt(1.5)
    tf = box_when_af.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.28)
    tf.margin_right = Inches(0.28)
    tf.margin_top = Inches(0.24)
    tf.margin_bottom = Inches(0.2)

    p = tf.paragraphs[0]
    p.text = "🎯 NÊN CHỌN AIRFLOW KHI:"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    for w_t, w_d in [
        ("Team đã có kinh nghiệm Airflow dày dặn:", "Tận dụng hạ tầng, kỹ năng và quy trình DevOps sẵn có."),
        ("Bài toán điều phối hạ tầng (Orchestration):", "Kích hoạt định kỳ các tác vụ dbt, EMR, Kubernetes Job, backup DB."),
        ("Hệ thống yêu cầu RBAC khắt khe On-Premise:", "Cần phân quyền truy cập DAG chi tiết cho từng người dùng/nhóm."),
        ("Ít quan tâm đến Data Lineage & Asset Quality:", "Quy trình ETL đơn giản, chuyển dữ liệu từ A sang B định kỳ."),
        ("Cần sự ổn định lâu dài:", "Thư viện plugin phong phú hỗ trợ gần như mọi dịch vụ công nghệ trên thị trường.")
    ]:
        pt = tf.add_paragraph()
        pt.text = f"• {w_t}"
        pt.font.name = FONT_MAIN
        pt.font.bold = True
        pt.font.size = Pt(11)
        pt.font.color.rgb = TEXT_MAIN
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = w_d
        pd.font.name = FONT_MAIN
        pd.font.size = Pt(9.8)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_before = Pt(2)

    box_when_dg = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c2_x, cards_y, col_w, cards_h)
    box_when_dg.fill.solid()
    box_when_dg.fill.fore_color.rgb = CARD_BG
    box_when_dg.line.color.rgb = ACCENT_PURPLE
    box_when_dg.line.width = Pt(1.5)
    tf = box_when_dg.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.28)
    tf.margin_right = Inches(0.28)
    tf.margin_top = Inches(0.24)
    tf.margin_bottom = Inches(0.2)

    p = tf.paragraphs[0]
    p.text = "🎯 NÊN CHỌN DAGSTER KHI:"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE

    for w_t, w_d in [
        ("Xây dựng Modern Data Platform / Data Mesh:", "Nơi tài sản dữ liệu, chất lượng dữ liệu và Data Catalog là ưu tiên hàng đầu."),
        ("Tập trung vào Tự động hóa Kiểm thử (Testing):", "Muốn kiểm thử toàn bộ pipeline trong CI/CD trước khi đưa lên production."),
        ("Pipeline xử lý dữ liệu phức tạp & AI/ML:", "Cần theo dõi Data Lineage, phân nhánh theo chất lượng dữ liệu như bài toán hóa đơn."),
        ("Môi trường phát triển đa đội ngũ:", "Nhiều team cùng phát triển trên các Code Server cô lập, không ảnh hưởng lẫn nhau."),
        ("Muốn trải nghiệm phát triển (DevX) vượt trội:", "Giao diện hiện đại, trực quan, hỗ trợ reload code chỉ với một cú click.")
    ]:
        pt = tf.add_paragraph()
        pt.text = f"• {w_t}"
        pt.font.name = FONT_MAIN
        pt.font.bold = True
        pt.font.size = Pt(11)
        pt.font.color.rgb = TEXT_MAIN
        pt.space_before = Pt(8)

        pd = tf.add_paragraph()
        pd.text = w_d
        pd.font.name = FONT_MAIN
        pd.font.size = Pt(9.8)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_before = Pt(2)

    add_speaker_notes(s9, "Speaker Note: Đưa ra lời khuyên thực tiễn cho ban lãnh đạo và các nhóm kỹ thuật: lựa chọn công cụ dựa trên bài toán cụ thể chứ không theo trào lưu.")

    # =========================================================================
    # SLIDE 10: LỘ TRÌNH TRIỂN KHAI 3 GIAI ĐOẠN
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Kế Hoạch Hành Động", "Lộ Trình Triển Khai Chuyển Đổi 3 Giai Đoạn",
               "Chiến lược chuyển đổi khả thi giúp giảm thiểu rủi ro gián đoạn hệ thống")

    col_3_w = Inches(3.644)
    gap_3 = Inches(0.4)
    start_3_x = Inches(0.8)

    phases = [
        ("GIAI ĐOẠN 1 (Tháng 1-2)", "THỬ NGHIỆM (POC)", ACCENT_CYAN, [
            "Triển khai cụm thử nghiệm (Local / Dev K8s).",
            "Chạy song song kịch bản xử lý Invoice PDF trên cả 2 công cụ.",
            "Đo lường thời gian test CI/CD và độ ổn định khi tải tăng.",
            "Thu thập đánh giá trải nghiệm thực tế từ các kỹ sư dữ liệu."
        ]),
        ("GIAI ĐOẠN 2 (Tháng 3-4)", "HYBRID CO-EXISTENCE", ACCENT_AMBER, [
            "Tận dụng Airflow điều phối các tác vụ hạ tầng và hệ thống cũ.",
            "Sử dụng Dagster cho các pipeline bóc tách dữ liệu mới và AI/ML.",
            "Đồng bộ hóa lưu trữ artifacts qua MinIO On-Premise chung.",
            "Xây dựng bộ quy chuẩn CI/CD và tiêu chuẩn viết Asset Checks."
        ]),
        ("GIAI ĐOẠN 3 (Tháng 5+)", "CHUYỂN DỊCH HOÀN TOÀN", ACCENT_GREEN, [
            "Di chuyển toàn bộ pipeline nghiệp vụ quan trọng sang nền tảng chuẩn hóa.",
            "Hoàn thiện hệ thống giám sát cảnh báo (Prometheus, Grafana).",
            "Đóng gói tài liệu bàn giao, đào tạo nội bộ và tối ưu hóa chi phí On-Prem.",
            "Tự tin mở rộng quy mô xử lý hàng triệu hóa đơn/tháng."
        ])
    ]

    for idx, (p_phase, p_sub, p_color, p_items) in enumerate(phases):
        px = start_3_x + (col_3_w + gap_3) * idx
        card = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, cards_y, col_3_w, cards_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = p_color
        card.line.width = Pt(1.5)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.24)
        tf.margin_right = Inches(0.24)
        tf.margin_top = Inches(0.24)
        tf.margin_bottom = Inches(0.2)

        p = tf.paragraphs[0]
        p.text = p_phase
        p.font.name = FONT_MAIN
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = p_color

        p_s = tf.add_paragraph()
        p_s.text = p_sub
        p_s.font.name = FONT_MAIN
        p_s.font.size = Pt(11)
        p_s.font.bold = True
        p_s.font.color.rgb = TEXT_MAIN
        p_s.space_before = Pt(2)

        for it in p_items:
            pt = tf.add_paragraph()
            pt.text = f"• {it}"
            pt.font.name = FONT_MAIN
            pt.font.size = Pt(10.5)
            pt.font.color.rgb = TEXT_MUTED
            pt.space_before = Pt(12)

    add_speaker_notes(s10, "Speaker Note: Trình bày kế hoạch 3 giai đoạn: POC -> Chạy song song (Hybrid) -> Chuyển dịch toàn diện. Tránh rủi ro 'Big Bang' làm gián đoạn sản xuất.")

    # =========================================================================
    # SLIDE 11: TỔNG KẾT & Q&A
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Kết Luận & Thảo Luận", "Tổng Kết & Thảo Luận (Q&A)",
               "Thông điệp cốt lõi và sẵn sàng giải đáp thắc mắc chuyên sâu")

    # Top Section: 3 Executive Message Cards
    msg_top_y = Inches(1.68)
    msg_card_h = Inches(1.08)
    msg_gap = Inches(0.12)
    full_card_w = Inches(11.733)

    messages = [
        ("1. Không có công cụ 'hoàn hảo nhất', chỉ có công cụ 'phù hợp nhất':",
         "Airflow vững chãi cho điều phối hạ tầng truyền thống; Dagster vượt trội cho kỹ thuật dữ liệu hiện đại và kiểm soát chất lượng.",
         ACCENT_CYAN),
        ("2. Asset-Centric là tương lai của Quản trị Dữ liệu:",
         "Tư duy lấy dữ liệu làm trung tâm giúp doanh nghiệp kiểm soát tính toàn vẹn, data lineage và sẵn sàng cho các bài toán AI/LLM.",
         ACCENT_PURPLE),
        ("3. Tự chủ On-Premise tối ưu chi phí và bảo mật:",
         "Kết hợp Kubernetes và MinIO giúp doanh nghiệp kiểm soát 100% dữ liệu nhạy cảm mà không bị phụ thuộc vào hóa đơn điện toán đám mây.",
         ACCENT_GREEN)
    ]

    for idx, (m_t, m_d, m_col) in enumerate(messages):
        card_m = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), msg_top_y + (msg_card_h + msg_gap) * idx,
                                      full_card_w, msg_card_h)
        card_m.fill.solid()
        card_m.fill.fore_color.rgb = CARD_BG
        card_m.line.color.rgb = m_col
        card_m.line.width = Pt(1.2)
        tf = card_m.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.24)
        tf.margin_right = Inches(0.24)
        tf.margin_top = Inches(0.12)
        tf.margin_bottom = Inches(0.1)

        p = tf.paragraphs[0]
        p.text = m_t
        p.font.name = FONT_MAIN
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = m_col

        pd = tf.add_paragraph()
        pd.text = m_d
        pd.font.name = FONT_MAIN
        pd.font.size = Pt(10.5)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_before = Pt(3)

    # Bottom Section: Dedicated Q&A & Appreciation Banner
    banner_y = Inches(5.38)
    banner_h = Inches(1.58)
    qa_banner = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), banner_y, full_card_w, banner_h)
    qa_banner.fill.solid()
    qa_banner.fill.fore_color.rgb = CARD_BG
    qa_banner.line.color.rgb = BORDER_PURPLE
    qa_banner.line.width = Pt(1.5)
    tf_qa = qa_banner.text_frame
    tf_qa.word_wrap = True
    tf_qa.vertical_anchor = MSO_ANCHOR.MIDDLE

    p_qa = tf_qa.paragraphs[0]
    p_qa.text = "💬 SẴN SÀNG TRẢ LỜI CÂU HỎI (Q&A)"
    p_qa.font.name = FONT_MAIN
    p_qa.font.size = Pt(21)
    p_qa.font.bold = True
    p_qa.font.color.rgb = ACCENT_GREEN
    p_qa.alignment = PP_ALIGN.CENTER

    p_thanks = tf_qa.add_paragraph()
    p_thanks.text = "Xin chân thành cảm ơn quý anh chị đã lắng nghe!"
    p_thanks.font.name = FONT_MAIN
    p_thanks.font.size = Pt(13)
    p_thanks.font.color.rgb = TEXT_MAIN
    p_thanks.alignment = PP_ALIGN.CENTER
    p_thanks.space_before = Pt(6)

    add_speaker_notes(s11, "Speaker Note: Tóm tắt 3 kết luận chính và mời ban lãnh đạo cùng các đồng nghiệp đặt câu hỏi thảo luận.")

    # Save presentation
    output_filename = "Airflow_vs_Dagster_Thuyet_Trinh.pptx"
    prs.save(output_filename)
    print(f"Presentation generated successfully: {output_filename}")

if __name__ == "__main__":
    create_presentation()
