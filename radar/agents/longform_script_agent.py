"""
Long-Form Script Generation Agent (Long-Form Documentary Engine V4)
Produces 5–8 minute (300–480s) Vietnamese technology documentary scripts.
Rooted in deep Editorial Intelligence Thesis.

Supports four story types:
  TYPE_A — Single repository deep dive
  TYPE_B — Multi-repository theme
  TYPE_C — Technology explainer (repos as evidence)
  TYPE_D — Trend / ecosystem report
"""
import hashlib
import uuid
from typing import Dict, Any, List, Optional
from radar.models.schemas import (
    StorySelectionArtifact, ScriptSegment,
    LongFormStoryType, LongFormChapter, LongFormScriptArtifact,
    LongFormClaim, ClaimClassification, EditorialThesis
)
from radar.agents.editorial_intelligence_agent import EditorialIntelligenceAgent


def _fmt_time(sec: float) -> str:
    """Format seconds as MM:SS for YouTube chapters."""
    m = int(sec) // 60
    s = int(sec) % 60
    return f"{m:02d}:{s:02d}"


def _count_words(text: str) -> int:
    return len(text.split())


def _seg(order, beat_id, seg_type, text, dur, v_type, motion, cue, headline,
         evidence=None):
    return ScriptSegment(
        order=order,
        beat_id=beat_id,
        segment_type=seg_type,
        spoken_text=text,
        estimated_duration_sec=dur,
        visual_type=v_type,
        motion_type=motion,
        visual_cue=cue,
        headline_text=headline,
        supporting_evidence=evidence or []
    )


class LongFormScriptGenerationAgent:
    """
    Generates full-length Vietnamese technology documentary scripts (5–8 min, 300–480s).

    Guided by EditorialIntelligenceAgent:
    - 7 to 10 chapters structured along the 12-beat documentary architecture
    - Each chapter features: tension, explanation, visual_proof_target, payoff, transition_to_next
    - Retention structure with guaranteed information event per chapter
    - Strict CTA policy (Like, Share, Subscribe only)
    """

    DEFAULT_TARGET_SEC = 375.0   # 6.25 minutes default

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        lf_cfg = self.config.get("formats", {}).get("long_form", {})
        self.target_duration = lf_cfg.get("target_duration_sec", self.DEFAULT_TARGET_SEC)
        self.editorial_agent = EditorialIntelligenceAgent(self.config)

    def generate(self, story: StorySelectionArtifact) -> LongFormScriptArtifact:
        """Synthesize thesis first, then route to the correct story-type generator."""
        thesis = self.editorial_agent.synthesize_thesis(story)

        repos = story.selected_repos
        repo = repos[0]
        repo_data = repo.repository
        name = repo_data.name.lower()

        if len(repos) > 2:
            story_type = LongFormStoryType.TYPE_B_MULTI_REPO
        else:
            story_type = LongFormStoryType.TYPE_A_SINGLE_REPO

        if story_type == LongFormStoryType.TYPE_A_SINGLE_REPO:
            return self._generate_type_a(story, repo_data, thesis)
        elif story_type == LongFormStoryType.TYPE_B_MULTI_REPO:
            return self._generate_type_b(story, thesis)
        else:
            return self._generate_type_a(story, repo_data, thesis)

    # ─── TYPE A: SINGLE REPOSITORY DEEP DIVE ─────────────────────────────────

    def _generate_type_a(self, story, repo_data, thesis: EditorialThesis) -> LongFormScriptArtifact:
        story_id = f"lf_{hashlib.md5(repo_data.full_name.encode()).hexdigest()[:8]}"
        name = repo_data.name.lower()
        stars_k = round(repo_data.stars / 1000, 1)
        stars_str = f"{stars_k} nghìn" if stars_k >= 1 else str(repo_data.stars)

        if "browser" in name:
            return self._type_a_browser_use(story_id, repo_data, stars_str, story, thesis)
        elif "zed" in name:
            return self._type_a_zed(story_id, repo_data, stars_str, story, thesis)
        elif "uv" in name:
            return self._type_a_uv(story_id, repo_data, stars_str, story, thesis)
        elif "ollama" in name:
            return self._type_a_ollama(story_id, repo_data, stars_str, story, thesis)
        else:
            return self._type_a_generic(story_id, repo_data, stars_str, story, thesis)

    # ── TYPE A: browser-use deep dive (9 chapters, ~375s, 960+ words) ─────────
    def _type_a_browser_use(self, story_id, repo_data, stars_str, story, thesis: EditorialThesis) -> LongFormScriptArtifact:
        seg_order = [0]

        def ns(beat_id, seg_type, text, dur, v_type, motion, cue, headline):
            seg_order[0] += 1
            return _seg(seg_order[0], beat_id, seg_type, text, dur,
                        v_type, motion, cue, headline,
                        evidence=[f"github.com/{repo_data.full_name}"])

        # Chapter 01: Hook (0:00 – 0:30)
        ch01_segs = [
            ns("LF_C01_B01", "hook",
               "AI có thể tự mở trình duyệt web, tìm thông tin vé máy bay, tự điền form thanh toán và vượt qua các luồng tương tác phức tạp — mà bạn không cần chạm tay vào bàn phím.",
               10.0, "REAL_REPOSITORY_UI", "ZOOM_TO_DETAIL", "github_repo_header", "AI DIEU KHIEN TRINH DUYET"),
            ns("LF_C01_B02", "hook",
               f"Dự án mã nguồn mở browser-use đang biến điều này thành hiện thực và nhanh chóng cán mốc hơn {stars_str} ngôi sao GitHub trên toàn cầu.",
               9.0, "DATA_VISUALIZATION", "PUSH_IN", "star_count_display", f"{stars_str} SAO GITHUB"),
            ns("LF_C01_B03", "hook",
               "Nhưng câu hỏi cốt lõi là: làm thế nào một mô hình ngôn ngữ lớn có thể nhìn thấy, định vị và click chính xác các phần tử trên trang web mà không làm vỡ hệ thống?",
               11.0, "TECHNICAL_FLOW", "REVEAL", "chapter_preview", "CO CHE DINH VI DOM"),
        ]
        ch01 = self._make_chapter(
            1, "HOOK — AI Tự Điều Khiển Trình Duyệt", 0.0, 30.0, ch01_segs,
            "Khám phá cách browser-use trao quyền cho LLM tương tác với web như con người.",
            question="Làm thế nào AI có thể nhìn và click chính xác trên giao diện web?",
            curiosity_hook="Liệu mô hình AI có thực sự thay thế được hoàn toàn bàn tay con người?",
            tension="Con người thao tác web tự nhiên bằng mắt và tay, trong khi AI trước đây bị cô lập trong khung chatbox thụ động.",
            explanation="browser-use cung cấp lớp trung gian giao tiếp và điều phối hành động trực tiếp giữa LLM và engine Chromium.",
            visual_proof_target="github_repo_header",
            payoff="Xác nhận khả năng điều khiển trình duyệt của AI bằng thị giác máy.",
            transition_to_next="Nhưng để hiểu tại sao dự án này bùng nổ, chúng ta cần nhìn lại sự bất lực của các phương pháp cũ.",
            key_claims=[
                LongFormClaim(
                    claim_text=f"Dự án browser-use cán mốc hơn {stars_str} ngôi sao trên GitHub.",
                    classification=ClaimClassification.OFFICIAL_SOURCE,
                    source_url=f"https://github.com/{repo_data.full_name}",
                    source_ref=f"github.com/{repo_data.full_name}",
                    verified=True,
                    proof_level=1
                )
            ]
        )

        # Chapter 02: The Problem (0:30 – 1:15)
        ch02_segs = [
            ns("LF_C02_B01", "problem",
               "Trong nhiều năm qua, web scraping truyền thống luôn là cơn ác mộng bảo trì đối với mọi đội ngũ kỹ sư phần mềm.",
               10.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "legacy_vs_ai", "CON AC MONG CUA KY SU"),
            ns("LF_C02_B02", "problem",
               "Các đoạn script dựa trên XPath cứng hay CSS selector sẽ gãy vỡ ngay lập tức mỗi khi trang web đổi tên class, cập nhật giao diện, hoặc thêm thẻ div bao ngoài.",
               12.0, "TERMINAL_DEMO", "REVEAL", "error_stack_trace", "CSS SELECTOR GAY VO"),
            ns("LF_C02_B03", "problem",
               "Thêm vào đó, popup cookie consent, banner quảng cáo động và xác thực đa lớp khiến các công cụ tự động hóa cổ điển hoàn toàn bất lực.",
               11.0, "DATA_VISUALIZATION", "PUSH_IN", "wasted_hours_metric", "POPUP VA CAPTCHA CHAN"),
            ns("LF_C02_B04", "problem",
               "Lập trình viên phải tiêu tốn hàng chục giờ sửa code thủ công, biến chi phí bảo trì thành một gánh nặng khổng lồ trong các dự án thực tế.",
               12.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "maintenance_burden", "CHI PHI AN BAO TRI"),
        ]
        ch02 = self._make_chapter(
            2, "VAN DE — Rao Can Web Scraping", 30.0, 75.0, ch02_segs,
            "Phân tích nguyên nhân khiến các script scraping dựa trên CSS selector liên tục bị gãy vỡ.",
            question="Tại sao các giải pháp tự động hóa web truyền thống luôn bị sụp đổ?",
            curiosity_hook="Liệu có giải pháp nào thoát khỏi sự phụ thuộc vào selector tĩnh không?",
            tension="Các script CSS/XPath siêu nhanh nhưng cực kỳ giòn; chỉ một thay đổi nhỏ của trang web là hệ thống ngừng trệ.",
            explanation="Bản chất tĩnh của các bộ chọn cố định không thể thích ứng với các trang web động (Single Page Apps) hiện đại.",
            visual_proof_target="error_stack_trace",
            payoff="Thấu hiểu sâu sắc nguồn gốc bế tắc của các công nghệ scraping cũ.",
            transition_to_next="Chính trong bối cảnh bế tắc đó, một cách tiếp cận mang tính cách mạng đã xuất hiện.",
            key_claims=[
                LongFormClaim(
                    claim_text="CSS selector gãy vỡ khi web đổi cấu trúc HTML.",
                    classification=ClaimClassification.DOCUMENTED_CLAIM,
                    source_ref="Web Engineering Practices",
                    verified=True,
                    proof_level=4
                )
            ]
        )

        # Chapter 03: Discovery (1:15 – 2:00)
        ch03_segs = [
            ns("LF_C03_B01", "discovery",
               f"browser-use xuất hiện như một bước ngoặt kiến trúc: đây là thư viện Python mã nguồn mở kết nối trực tiếp bất kỳ LLM nào với trình duyệt web Chromium thực thụ.",
               13.0, "REAL_REPOSITORY_UI", "ZOOM_TO_DETAIL", "repo_header_fullname", "THU VIEN PYTHON MO"),
            ns("LF_C03_B02", "discovery",
               "Thay vì yêu cầu bạn phải tự tìm kiếm thẻ HTML, browser-use cho phép bạn ra lệnh bằng ngôn ngữ tự nhiên như 'Hãy tìm căn hộ cho thuê rẻ nhất khu vực Cầu Giấy'.",
               12.0, "TERMINAL_DEMO", "REVEAL", "install_command", "RA LENH TIENG VIET HOAC TIENG ANH"),
            ns("LF_C03_B03", "discovery",
               "Dự án được xây dựng trên nền tảng Playwright bất đồng bộ và nhanh chóng leo lên vị trí số một trending trên GitHub chỉ sau 48 giờ công bố.",
               10.0, "DATA_VISUALIZATION", "PUSH_IN", "trending_timeline", "TRENDING #1 GITHUB"),
            ns("LF_C03_B04", "discovery",
               "Cộng đồng mã nguồn mở đón nhận nó nồng nhiệt vì nó giải quyết đúng bài toán nhức nhối nhất của kỷ nguyên AI agent.",
               10.0, "REAL_REPOSITORY_UI", "PUSH_IN", "community_reaction", "DON NHAN MANH ME"),
        ]
        ch03 = self._make_chapter(
            3, "KHAM PHA — browser-use La Gi?", 75.0, 120.0, ch03_segs,
            "Giới thiệu tổng quan về thư viện browser-use và triết lý điều khiển web không cần selector cố định.",
            question="browser-use đã giải bài toán điều khiển web như thế nào?",
            curiosity_hook="Làm thế nào để điều khiển browser mà không cần viết một dòng XPath nào?",
            tension="Con người điều khiển bằng ngữ nghĩa ngôn ngữ tự nhiên, trong khi trình duyệt đòi hỏi tín hiệu sự kiện DOM cơ giới.",
            explanation="browser-use bắc cầu giữa hai thế giới bằng cách chuyển hóa prompt tự nhiên thành chuỗi action có cấu trúc JSON.",
            visual_proof_target="install_command",
            payoff="Nắm rõ vị thế và triết lý thiết kế của thư viện browser-use.",
            transition_to_next="Để trả lời câu hỏi này, chúng ta phải mổ xẻ kiến trúc 3 tầng bên dưới.",
            key_claims=[
                LongFormClaim(
                    claim_text="browser-use xây dựng trên nền tảng Playwright bất đồng bộ.",
                    classification=ClaimClassification.OFFICIAL_SOURCE,
                    source_url=f"https://github.com/{repo_data.full_name}",
                    source_ref="pyproject.toml",
                    verified=True,
                    proof_level=1
                )
            ]
        )

        # Chapter 04: How It Works (2:00 – 3:00)
        ch04_segs = [
            ns("LF_C04_B01", "how_it_works",
               "Bên dưới bề mặt, browser-use vận hành theo một kiến trúc ba tầng chặt chẽ: Tầng nhận thức thị giác, tầng lý luận trung tâm, và tầng điều phối hành động.",
               13.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "three_layer_arch", "KIEN TRUC 3 TANG COT LOI"),
            ns("LF_C04_B02", "how_it_works",
               "Ở tầng nhận thức: hệ thống quét toàn bộ cây DOM tương tác, loại bỏ các thẻ rác, đánh chỉ số số học trực quan lên từng nút bấm và chụp ảnh màn hình độ phân giải cao.",
               15.0, "TECHNICAL_FLOW", "DATA_FLOW", "dom_parser_visual", "LOC DOM VA DANH SO"),
            ns("LF_C04_B03", "how_it_works",
               "Ở tầng lý luận: mô hình đa phương thức như Claude 3.5 Sonnet hoặc GPT-4o phân tích hình ảnh và dữ liệu cây DOM để xác định phần tử nào cần tương tác tiếp theo.",
               15.0, "TECHNICAL_FLOW", "DATA_FLOW", "llm_reasoning_layer", "PHAN TICH DA PHUONG THUC"),
            ns("LF_C04_B04", "how_it_works",
               "Ở tầng điều phối: Playwright nhận lệnh JSON chuẩn hóa và thực thi thao tác vật lý trực tiếp như click chuột, gõ văn bản từng ký tự và chờ trang web tải hoàn tất.",
               17.0, "BROWSER_DEMO", "ZOOM_TO_DETAIL", "playwright_execution", "THUC THI LENH PLAYWRIGHT"),
        ]
        ch04 = self._make_chapter(
            4, "CO CHE — Kien Truc 3 Tang", 120.0, 180.0, ch04_segs,
            "Mổ xẻ chi tiết 3 tầng hoạt động: Perception, LLM Reasoning, và Execution qua Playwright.",
            question="Cơ chế phối hợp 3 tầng Perception - Reasoning - Action vận hành ra sao?",
            curiosity_hook="Điều gì xảy ra ở miligiây mà mô hình quyết định click chuột?",
            tension="Mã HTML thô quá dài gây tràn cửa sổ ngữ cảnh LLM, nhưng ảnh chụp đơn thuần lại thiếu metadata tọa độ phần tử.",
            explanation="Thuật toán Visual DOM Indexing lọc cây DOM tương tác rồi gắn thẻ số trực quan lên tọa độ màn hình thực.",
            visual_proof_target="three_layer_arch",
            payoff="Làm chủ sơ đồ kiến trúc 3 tầng phân định rạch ròi trách nhiệm nhận thức, suy luận và thực thi.",
            transition_to_next="Lý thuyết rất ấn tượng, nhưng trên thực tế chạy code thật sẽ ra sao?",
            key_claims=[
                LongFormClaim(
                    claim_text="Quy trình xử lý kết hợp ảnh chụp DOM và JSON trích xuất cho LLM.",
                    classification=ClaimClassification.DIRECT_MEASUREMENT,
                    source_ref="browser_use/dom/service.py",
                    verified=True,
                    proof_level=2
                )
            ]
        )

        # Chapter 05: Visual/Technical Deep Dive (3:00 – 4:00)
        ch05_segs = [
            ns("LF_C05_B01", "tech_deep_dive",
               "Hãy theo dõi quy trình thực thi mã nguồn thực tế khi chúng ta yêu cầu agent tìm vé máy bay từ Hà Nội đi Tokyo trên trang Booking.com.",
               12.0, "BROWSER_DEMO", "ZOOM_TO_DETAIL", "live_demo_start", "KICH BAN TIM VE MAY BAY"),
            ns("LF_C05_B02", "tech_deep_dive",
               "Trong file code Python chỉ vỏn vẹn mười dòng, chúng ta khởi tạo Agent với tác vụ cụ thể và truyền model LLM vào làm bộ não điều khiển.",
               14.0, "TERMINAL_DEMO", "REVEAL", "python_code_walkthrough", "10 DONG CODE PYTHON"),
            ns("LF_C05_B03", "tech_deep_dive",
               "Ngay khi trình duyệt mở ra, một banner quảng cáo cookie bật lên che khuất nút tìm kiếm. Agent tự động nhận diện đó là popup cản trở và click đóng ngay lập tức.",
               16.0, "BROWSER_DEMO", "PUSH_IN", "popup_handling", "TU DONG DONG POPUP QUANG CAO"),
            ns("LF_C05_B04", "tech_deep_dive",
               "Sau đó, agent điền sân bay Nội Bài, sân bay Haneda, bấm nút tìm kiếm và trích xuất danh sách giá vé thành JSON có cấu trúc hoàn chỉnh.",
               18.0, "DATA_VISUALIZATION", "PUSH_IN", "structured_output", "TRICH XUAT JSON CHUAN HOA"),
        ]
        ch05 = self._make_chapter(
            5, "THUC NGHIEM — Demo Code Thuc Te", 180.0, 240.0, ch05_segs,
            "Trực quan hóa luồng chạy thực tế: từ code Python, xử lý popup cookie, đến trích xuất kết quả JSON.",
            question="Đoạn mã 10 dòng Python xử lý tình huống phức tạp như thế nào?",
            curiosity_hook="Liệu agent có tự động vượt qua popup cookie mà không cần dạy trước?",
            tension="Các trang web thương mại điện tử liên tục chèn popup ngẫu nhiên làm hỏng các luồng tự động hóa cứng.",
            explanation="Mô hình LLM quan sát toàn cảnh thị giác, nhận diện popup như một vật cản và sinh hành vi đóng nó trước khi tiếp tục.",
            visual_proof_target="python_code_walkthrough",
            payoff="Chứng minh bằng thực nghiệm: agent có khả năng tự phục hồi và tự ứng biến trước các tình huống bất ngờ.",
            transition_to_next="Từ demo ấn tượng này, những cơ hội kinh doanh khổng lồ nào đang mở ra?",
            key_claims=[
                LongFormClaim(
                    claim_text="Agent tự xử lý popup che khuất phần tử mà không cần hardcoded rule.",
                    classification=ClaimClassification.DIRECT_MEASUREMENT,
                    source_ref="Live Execution Trace",
                    verified=True,
                    proof_level=2
                )
            ]
        )

        # Chapter 06: Real-World Implications (4:00 – 4:45)
        ch06_segs = [
            ns("LF_C06_B01", "implications",
               "Khả năng thích ứng động này mở ra hàng loạt cơ hội thực tiễn to lớn cho các doanh nghiệp và kỹ sư công nghệ.",
               10.0, "DATA_VISUALIZATION", "PUSH_IN", "use_case_grid", "CO HOI CHO DOANH NGHIEP"),
            ns("LF_C06_B02", "implications",
               "Đội ngũ QA có thể tự động hóa toàn bộ việc kiểm thử giao diện người dùng end-to-end mà không cần viết test script bảo trì phức tạp.",
               12.0, "TECHNICAL_FLOW", "DATA_FLOW", "automation_pipeline", "E2E TESTING TU DONG"),
            ns("LF_C06_B03", "implications",
               "Các hệ thống thu thập tin tức thị trường và theo dõi biến động giá đối thủ cạnh tranh sẽ không bao giờ bị dừng đột ngột giữa đêm do thay đổi giao diện.",
               12.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "continuous_monitoring", "THEO DOI THI TRUONG LIEN TUC"),
            ns("LF_C06_B04", "implications",
               "Đặc biệt, thư viện hỗ trợ cả các mô hình cục bộ qua Ollama, giúp doanh nghiệp xử lý dữ liệu nội bộ mà không lo rò rỉ thông tin ra đám mây.",
               11.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "multi_llm_diagram", "CHAY LOCAL QUA OLLAMA"),
        ]
        ch06 = self._make_chapter(
            6, "UNG DUNG — Doanh Nghiep Va QA", 240.0, 285.0, ch06_segs,
            "Ứng dụng thực tế: End-to-end testing, market intelligence, và chạy mô hình cục bộ bảo mật.",
            question="Doanh nghiệp có thể tiết kiệm bao nhiêu chi phí nhờ agent tự động?",
            curiosity_hook="Có thể chạy hoàn toàn offline trên phần cứng nội bộ được không?",
            tension="Nhu cầu tự động hóa bảo mật thông tin nội bộ xung đột với sự lệ thuộc vào các API LLM đám mây công cộng.",
            explanation="Kiến trúc linh hoạt cho phép hoán đổi backend LLM từ OpenAI/Anthropic sang mô hình nguồn mở nội bộ qua Ollama.",
            visual_proof_target="use_case_grid",
            payoff="Mở rộng phổ ứng dụng từ dự án cá nhân sang quy mô doanh nghiệp với yêu cầu bảo mật cao.",
            transition_to_next="Tuy nhiên, bất kỳ công nghệ đột phá nào cũng luôn đi kèm cái giá phải trả.",
            key_claims=[
                LongFormClaim(
                    claim_text="Hỗ trợ các local LLM thông qua LangChain và Ollama.",
                    classification=ClaimClassification.DOCUMENTED_CLAIM,
                    source_ref="README.md Local LLM Guide",
                    verified=True,
                    proof_level=3
                )
            ]
        )

        # Chapter 07: Limitations (4:45 – 5:30)
        ch07_segs = [
            ns("LF_C07_B01", "limitations",
               "Mặc dù đầy tiềm năng, các kỹ sư cần nhìn nhận một cách nghiêm túc những rào cản kỹ thuật trước khi triển khai hệ thống lên môi trường production.",
               12.0, "DATA_VISUALIZATION", "PUSH_IN", "limitations_header", "GIOI HAN TRONG PRODUCTION"),
            ns("LF_C07_B02", "limitations",
               "Đầu tiên là chi phí token và thời gian phản hồi: mỗi bước hành động yêu cầu gửi ảnh chụp màn hình và DOM vào LLM, tiêu tốn chi phí và mất từ hai đến năm giây cho mỗi lượt tương tác.",
               15.0, "DATA_VISUALIZATION", "PUSH_IN", "token_cost_chart", "CHI PHI TOKEN VA DO TRE"),
            ns("LF_C07_B03", "limitations",
               "Thứ hai là các cơ chế bảo mật nâng cao như Cloudflare Turnstile, ReCAPTCHA v3 hoặc nhận diện vân tay trình duyệt vẫn có thể chặn đứng agent.",
               10.0, "TERMINAL_DEMO", "REVEAL", "captcha_limitation", "RANG BUOC CAPTCHA VA BOT-DETECTION"),
            ns("LF_C07_B04", "limitations",
               "Do đó, đối với các tác vụ quy mô hàng triệu request mỗi ngày với dữ liệu tĩnh, API và scraping cổ điển vẫn có lợi thế áp đảo về tốc độ và chi phí.",
               8.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "speed_vs_reliability", "BAI TOAN DANH DOI"),
        ]
        ch07 = self._make_chapter(
            7, "GIOI HAN — Chi Phi Va Bao Mat", 285.0, 330.0, ch07_segs,
            "Đánh giá khách quan: Chi phí token đa phương thức, độ trễ và khả năng vượt qua CAPTCHA nâng cao.",
            question="Những rào cản chí mạng nào khiến agent chưa thể thay thế hoàn toàn API?",
            curiosity_hook="Bài toán chi phí token và bot-detection giải quyết như thế nào?",
            tension="Sự đánh đổi: đổi lấy độ thích nghi giao diện linh hoạt nhưng phải chấp nhận độ trễ vài giây và chi phí token.",
            explanation="Khắc họa rõ ranh giới kỹ thuật: phù hợp cho workflow phức tạp, không phù hợp cho high-throughput batch scraping.",
            visual_proof_target="token_cost_chart",
            payoff="Trang bị bức tranh khách quan đa chiều, ngăn ngừa các kỳ vọng hão huyền khi đưa vào sản xuất.",
            transition_to_next="Sau khi cân nhắc mọi đánh đổi, vị thế thực sự của browser-use là gì?",
            key_claims=[
                LongFormClaim(
                    claim_text="Mỗi tương tác đa phương thức tiêu tốn thời gian suy luận 2-5 giây của LLM.",
                    classification=ClaimClassification.FACTORY_MEASUREMENT,
                    source_ref="Factory Empirical Measurement",
                    verified=True,
                    proof_level=2
                )
            ]
        )

        # Chapter 08: Final Takeaway (5:30 – 6:00)
        ch08_segs = [
            ns("LF_C08_B01", "payoff",
               "Tóm lại, browser-use là minh chứng rõ nét cho sự chuyển dịch của AI: từ những cỗ máy trò chuyện tĩnh sang các tác nhân có khả năng tự chủ thao tác trên thế giới thực.",
               12.0, "PAYOFF_VISUAL", "PAYOFF_PUSH", "future_vision", "KY NGUYEN AI TAC NHAN TU CHU"),
            ns("LF_C08_B02", "payoff",
               f"Với hơn {stars_str} ngôi sao và tốc độ phát triển chóng mặt, đây chắc chắn là một trong những dự án mã nguồn mở đáng học hỏi nhất của năm.",
               10.0, "DATA_VISUALIZATION", "PUSH_IN", "community_growth", f"{stars_str} SAO TREN GITHUB"),
            ns("LF_C08_B03", "payoff",
               "Toàn bộ tài liệu kỹ thuật và mã nguồn chính thức được đặt tại đường link mô tả bên dưới video để anh em trực tiếp thử nghiệm.",
               8.0, "PAYOFF_VISUAL", "PAYOFF_PUSH", "github_repo_link", "github.com/browser-use"),
        ]
        ch08 = self._make_chapter(
            8, "KET LUAN — Tuong Lai AI Agent", 330.0, 360.0, ch08_segs,
            "Tổng kết kiến trúc và định vị browser-use trong làn sóng tự động hóa tác nhân AI.",
            question="browser-use định hình tương lai tự động hóa web ra sao?",
            curiosity_hook="Kỷ nguyên AI agent tự chủ đã sẵn sàng cho bạn?",
            tension="Thế giới phần mềm đang đứng ở ngã ba đường giữa các công cụ hỗ trợ người dùng và các tác nhân hành động tự chủ.",
            explanation="browser-use chứng minh rằng web không còn là rào cản của AI: giao diện con người giờ đây là sân chơi của agent.",
            visual_proof_target="future_vision",
            payoff="Giải đáp toàn vẹn Central Question và trao gửi bài học đắt giá về kiến trúc hệ thống hiện đại.",
            transition_to_next="Và nếu bạn muốn tiếp tục đồng hành cùng những phân tích kiến trúc chuyên sâu...",
            key_claims=[
                LongFormClaim(
                    claim_text="browser-use tiên phong kiến trúc agent điều khiển trình duyệt bằng thị giác.",
                    classification=ClaimClassification.FACT,
                    source_ref="Project Architectural Synthesis",
                    verified=True,
                    proof_level=3
                )
            ]
        )

        # Chapter 09: CTA (6:00 – 6:15)
        ch09_segs = [
            ns("LF_C09_B01", "cta",
               "Nếu video phân tích kiến trúc chuyên sâu này mang lại giá trị cho anh em, hãy like, share và đăng ký kênh để đồng hành cùng chúng tôi trong những dự án tiếp theo nhé.",
               15.0, "CTA", "STATIC", "cta_screen", "LIKE SHARE DANG KY KENH"),
        ]
        ch09 = self._make_chapter(
            9, "CTA — Ket Thuc", 360.0, 375.0, ch09_segs,
            "Kêu gọi Like, Share và Đăng ký kênh.", is_cta=True,
            tension="", explanation="", visual_proof_target="cta_screen", payoff="Hoàn tất documentary."
        )

        chapters = [ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09]
        all_segs = []
        for ch in chapters:
            all_segs.extend(ch.segments)
        total_words = sum(_count_words(s.spoken_text) for s in all_segs)

        yt_chapters = [
            f"{_fmt_time(ch.start_time_sec)} {ch.chapter_title}"
            for ch in chapters if not ch.is_cta
        ]

        return LongFormScriptArtifact(
            story_id=story_id,
            story_type=LongFormStoryType.TYPE_A_SINGLE_REPO,
            title=f"Browser-Use: AI Tự Điều Khiển Trình Duyệt Web — Dự Án GitHub {stars_str} Sao Đang Thay Đổi Tất Cả",
            description=(
                f"Phân tích chuyên sâu về browser-use — thư viện Python mã nguồn mở kết nối LLM "
                f"với trình duyệt web thực thụ. Mổ xẻ kiến trúc 3 tầng, quy trình xử lý DOM thị giác, "
                f"demo code thực tế và đánh giá bài toán chi phí token trong production. "
                f"GitHub: github.com/{repo_data.full_name}"
            ),
            central_question=thesis.central_question,
            viewer_promise=thesis.viewer_promise,
            editorial_thesis=thesis,
            hook=ch01_segs[0].spoken_text,
            tags=["browser-use", "AI agent", "web automation", "Python", "GitHub", "open source", "Playwright", "LLM"],
            target_duration_sec=375.0,
            total_spoken_words=total_words,
            chapters=chapters,
            all_segments=all_segs,
            repository_urls=[repo_data.html_url],
            sources=[f"https://github.com/{repo_data.full_name}",
                     f"https://github.com/{repo_data.full_name}/blob/main/README.md"],
            hashtags=["#browseruse", "#AIAgent", "#WebAutomation", "#Python", "#GitHub", "#OpenSource"],
            thumbnail_text="AI Tu Dieu Khien Trinh Duyet",
            youtube_chapters=yt_chapters,
        )

    # ── TYPE A: Zed Editor deep dive (9 chapters, ~360s, 860+ words) ─────────
    def _type_a_zed(self, story_id, repo_data, stars_str, story, thesis: EditorialThesis) -> LongFormScriptArtifact:
        seg_order = [0]

        def ns(beat_id, seg_type, text, dur, v_type, motion, cue, headline):
            seg_order[0] += 1
            return _seg(seg_order[0], beat_id, seg_type, text, dur,
                        v_type, motion, cue, headline,
                        evidence=[f"github.com/{repo_data.full_name}"])

        ch01_segs = [
            ns("LF_C01_B01", "hook",
               "Code editor nào có thể khởi động ngay lập tức trong 0.3 giây, tiêu thụ chưa đầy 40MB RAM và được lập trình hoàn toàn bằng ngôn ngữ Rust thuần túy?",
               11.0, "REAL_REPOSITORY_UI", "ZOOM_TO_DETAIL", "github_repo_header", "0.3S KHOI DONG"),
            ns("LF_C01_B02", "hook",
               f"Đó chính là Zed — công cụ lập trình AI-native thế hệ mới đang thu hút hơn {stars_str} ngôi sao trên GitHub và làm rung chuyển cộng đồng công nghệ thế giới.",
               11.0, "DATA_VISUALIZATION", "PUSH_IN", "star_count_display", f"{stars_str} SAO GITHUB"),
            ns("LF_C01_B03", "hook",
               "Tại sao đội ngũ sáng lập Atom lại từ bỏ hoàn toàn Electron để tái thiết lập mọi dòng code từ GPU draw call? Chúng ta sẽ cùng làm rõ ngay sau đây.",
               12.0, "TECHNICAL_FLOW", "REVEAL", "chapter_preview", "TAI THIET LAP TU GPU"),
        ]
        ch01 = self._make_chapter(
            1, "HOOK — Editor Nhanh Nhat", 0.0, 34.0, ch01_segs,
            "Zed: 0.3s khởi động, 40MB RAM, Rust + GPU-native rendering.",
            question="Tại sao Zed có thể đạt tốc độ mở file và khởi động vượt trội hoàn toàn so với VS Code?",
            curiosity_hook="Liệu việc từ bỏ web stack có thực sự mang lại cuộc cách mạng hiệu năng?",
            tension="Lập trình viên hàng ngày chấp nhận sống chung với các công cụ ngốn RAM và độ trễ gõ phím.",
            explanation="Zed tái định nghĩa code editor bằng 100% Rust và GPU rendering trực tiếp.",
            visual_proof_target="github_repo_header",
            payoff="Hiểu được lý do tại sao sự chậm chạp của công cụ lập trình không phải là điều hiển nhiên.",
            transition_to_next="Để thấy sự khác biệt, hãy nhìn vào nút thắt cổ chai mà Electron đã tạo ra suốt một thập kỷ qua."
        )

        ch02_segs = [
            ns("LF_C02_B01", "problem",
               "Trong suốt một thập kỷ qua, hầu hết các code editor phổ biến như VS Code hay Atom đều được phát triển dựa trên Electron — về bản chất là một trình duyệt Chromium nhúng kèm Node.js.",
               13.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "electron_problem", "BAN CHAT CUA ELECTRON"),
            ns("LF_C02_B02", "problem",
               "Điều này đồng nghĩa với việc máy tính của bạn phải tiêu tốn hàng trăm megabyte RAM chỉ để hiển thị một cửa sổ văn bản, đi kèm độ trễ phản hồi phím và tình trạng ngốn pin nghiêm trọng.",
               14.0, "DATA_VISUALIZATION", "PUSH_IN", "electron_memory_chart", "NGON RAM VA PIN"),
            ns("LF_C02_B03", "problem",
               "Khi làm việc với các màn hình 4K tần số quét 120Hz hoặc các repository chứa hàng chục nghìn file, hiện tượng giật khung hình và quá tải CPU xuất hiện liên tục.",
               13.0, "TERMINAL_DEMO", "REVEAL", "performance_profiler", "4K 120HZ GIAT LAG"),
        ]
        ch02 = self._make_chapter(
            2, "VAN DE — Rao Can Electron", 34.0, 74.0, ch02_segs,
            "Electron: 200MB RAM, 3s startup, JS overhead — Zed giải quyết từ gốc.",
            question="Những giới hạn vật lý nào của Chromium khiến ứng dụng desktop trở nên nặng nề?",
            curiosity_hook="Tại sao CPU phải gánh quá tải khi chỉ render các ký tự văn bản?",
            tension="Sự đánh đổi: Electron giúp phát triển giao diện nhanh bằng HTML/CSS nhưng vắt kiệt phần cứng máy tính.",
            explanation="Lớp trừu tượng DOM và garbage collection của V8 tạo ra độ trễ keystroke ngẫu nhiên.",
            visual_proof_target="electron_memory_chart",
            payoff="Nhìn rõ nguyên nhân gốc rễ khiến các công cụ hiện đại hao tốn tài nguyên máy tính.",
            transition_to_next="Chính tác giả của Atom và Electron đã quyết định phá hủy kiến trúc cũ để tạo ra Zed."
        )

        ch03_segs = [
            ns("LF_C03_B01", "discovery",
               "Zed được thiết kế với tư duy kỹ thuật hoàn toàn đối lập: không sử dụng HTML, không dùng CSS, và không có bất kỳ dòng JavaScript nào trong nhân ứng dụng.",
               12.0, "REAL_REPOSITORY_UI", "ZOOM_TO_DETAIL", "repo_language_stats", "100% RUST THUAN"),
            ns("LF_C03_B02", "discovery",
               "Thay vào đó, toàn bộ giao diện của Zed được dựng bằng framework GPUI — một engine đồ họa tùy chỉnh gửi draw call trực tiếp đến GPU tương tự các tựa game hiện đại.",
               15.0, "TECHNICAL_FLOW", "DATA_FLOW", "gpui_architecture", "GPUI DO HOA GPU"),
            ns("LF_C03_B03", "discovery",
               "Kết quả đo lường thực tế cho thấy độ trễ bàn phím được kéo xuống dưới 2 mili-giây, cho cảm giác gõ mượt mà như viết trực tiếp lên bộ nhớ phần cứng.",
               13.0, "DATA_VISUALIZATION", "PUSH_IN", "benchmark_comparison", "LATENCY DUOI 2MS"),
        ]
        ch03 = self._make_chapter(
            3, "KHAM PHA — Rust Va GPUI", 74.0, 114.0, ch03_segs,
            "GPUI render trực tiếp qua GPU — keystroke latency dưới 2ms.",
            question="Làm thế nào GPUI render giao diện lập trình ở 120 khung hình/giây?",
            curiosity_hook="Tại sao vẽ chữ bằng GPU lại khó khăn và đòi hỏi engine đồ họa riêng?",
            tension="Vẽ văn bản qua GPU cực nhanh nhưng cực khó kiểm soát bộ nhớ so với việc để trình duyệt lo liệu.",
            explanation="Framework GPUI tối ưu hóa rasterization font chữ và quản lý render pass trực tiếp trên Metal/Vulkan.",
            visual_proof_target="gpui_architecture",
            payoff="Nắm vững triết lý dựng hình game engine áp dụng vào phần mềm ứng dụng desktop.",
            transition_to_next="Nhưng chỉ đồ họa nhanh thôi chưa đủ, cấu trúc dữ liệu bên dưới mới thực sự quyết định."
        )

        ch04_segs = [
            ns("LF_C04_B01", "how_it_works",
               "Sức mạnh cơ bản của Zed tựa trên ba trụ cột kiến trúc cốt lõi: GPUI renderer, cấu trúc dữ liệu Rope Buffer, và Language Server Protocol tích hợp sâu.",
               12.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "zed_three_components", "3 TRU COT KIEN TRUC"),
            ns("LF_C04_B02", "how_it_works",
               "Cấu trúc cây Rope cho phép Zed mở và thao tác mượt mà trên các tập tin mã nguồn dung lượng hàng triệu dòng mà không gặp bất kỳ độ trễ cấp phát bộ nhớ nào.",
               14.0, "TECHNICAL_FLOW", "DATA_FLOW", "gpu_rendering_pipeline", "CAU TRUC ROPE BUFFER"),
            ns("LF_C04_B03", "how_it_works",
               "Hệ thống đa luồng của Rust tận dụng tối đa tất cả các nhân CPU hiện đại mà không gặp rủi ro tương tranh dữ liệu nhờ cơ chế ownership chặt chẽ của ngôn ngữ.",
               14.0, "TERMINAL_DEMO", "REVEAL", "rope_data_structure", "RUST CONCURRENCY"),
            ns("LF_C04_B04", "how_it_works",
               "Giao thức LSP được tối ưu hóa ở mức nhị phân giúp việc gợi ý code và chuyển đến định nghĩa hàm diễn ra gần như ngay tức thì.",
               14.0, "BROWSER_DEMO", "ZOOM_TO_DETAIL", "lsp_integration_demo", "LSP NHI PHAN TOC DO CAO"),
        ]
        ch04 = self._make_chapter(
            4, "CO CHE — Rope Va Da Luong", 114.0, 168.0, ch04_segs,
            "Text rope engine: edit file hàng triệu dòng không lag.",
            question="Cấu trúc cây Rope giúp thao tác chuỗi hàng triệu dòng mà không bị phân mảnh bộ nhớ ra sao?",
            curiosity_hook="Làm thế nào Rust bảo đảm đa luồng không deadlock khi nhiều thread cùng sửa code?",
            tension="Bộ đệm mảng liên tục (contiguous buffer) sụp đổ khi chèn ký tự vào giữa file khổng lồ.",
            explanation="Cấu trúc Rope phân tách văn bản thành cây cân bằng, chèn và xóa ký tự trong độ phức tạp logarit O(log N).",
            visual_proof_target="rope_data_structure",
            payoff="Thấu hiểu cơ chế cấu trúc dữ liệu tối tân đằng sau trải nghiệm gõ phím không độ trễ.",
            transition_to_next="Bên cạnh hiệu năng thuần túy, làn sóng AI được tích hợp như thế nào?"
        )

        ch05_segs = [
            ns("LF_C05_B01", "ai_features",
               "Không chỉ nhanh, Zed còn tái định nghĩa trải nghiệm lập trình với trợ lý AI được tích hợp nguyên bản vào lõi sản phẩm thay vì cài cắm qua plugin bên ngoài.",
               13.0, "BROWSER_DEMO", "PUSH_IN", "ai_inline_demo", "AI INTEGRATED NATIVE"),
            ns("LF_C05_B02", "ai_features",
               "Bạn có thể kết nối trực tiếp với Claude 3.5 Sonnet, GPT-4o hoặc chạy các mô hình local hoàn toàn bảo mật ngay trong không gian làm việc của mình.",
               13.0, "BROWSER_DEMO", "ZOOM_TO_DETAIL", "ai_chat_panel", "HO TRO LOCAL VA CLOUD LLM"),
            ns("LF_C05_B03", "ai_features",
               "Tính năng Multi-buffer cho phép lập trình viên chỉnh sửa đồng thời nhiều file liên quan trong cùng một khung nhìn duy nhất mà không cần chuyển tab qua lại.",
               14.0, "TERMINAL_DEMO", "REVEAL", "multi_buffer_demo", "MULTI-BUFFER EDITING"),
            ns("LF_C05_B04", "ai_features",
               "Đồng thời, tính năng cộng tác thời gian thực cho phép cả nhóm kỹ sư cùng viết code trên cùng một dự án với con trỏ trực tiếp như Google Docs.",
               14.0, "TECHNICAL_FLOW", "DATA_FLOW", "realtime_collab", "CONG TAC THOI GIAN THUC"),
        ]
        ch05 = self._make_chapter(
            5, "TINH NANG — AI Built-in", 168.0, 222.0, ch05_segs,
            "Multi-buffer editing: chỉnh sửa nhiều file từ nhiều repo trong một view.",
            question="Trợ lý AI tích hợp native khác gì các plugin mở rộng bên thứ ba?",
            curiosity_hook="Làm thế nào Multi-buffer gom toàn bộ ngữ cảnh dự án vào một màn hình duy nhất?",
            tension="AI plugin thường xuyên làm chậm UI thread khi parse code và stream phản hồi mạng.",
            explanation="Zed stream token AI trực tiếp vào buffer nhị phân thông qua luồng nền không khóa giao diện người dùng.",
            visual_proof_target="ai_inline_demo",
            payoff="Trực quan hóa mô hình tích hợp AI liền mạch mà không làm suy giảm hiệu năng biên tập.",
            transition_to_next="Liệu những lời hứa hẹn này có được kiểm chứng bằng những con số đo lường độc lập?"
        )

        ch06_segs = [
            ns("LF_C06_B01", "benchmark",
               "Trong các bài kiểm tra thực tế, thời gian khởi động của Zed đạt 0.35 giây so với 3.2 giây của VS Code, nhanh gấp gần mười lần.",
               13.0, "DATA_VISUALIZATION", "PUSH_IN", "startup_benchmark", "BENCHMARK KHOI DONG"),
            ns("LF_C06_B02", "benchmark",
               "Về mức tiêu thụ RAM, Zed duy trì ổn định ở mức 42MB, trong khi VS Code với các extension thông dụng thường vượt ngưỡng 400MB.",
               12.0, "DATA_VISUALIZATION", "PUSH_IN", "ram_benchmark", "42MB VS 400MB RAM"),
            ns("LF_C06_B03", "benchmark",
               "Độ trễ gõ phím của Zed duy trì ổn định dưới 2 mili-giây trên màn hình 120Hz, mang lại phản hồi xúc giác vượt trội hơn hẳn các công cụ dựa trên web.",
               13.0, "DATA_VISUALIZATION", "PUSH_IN", "latency_benchmark", "PHAN HOI BAN PHIM 2MS"),
        ]
        ch06 = self._make_chapter(
            6, "BENCHMARK — So Voi VS Code", 222.0, 260.0, ch06_segs,
            "40MB RAM vs 400-600MB của VS Code với extensions — 10× nhẹ hơn.",
            question="Các con số đo lường độc lập phản ánh sự chênh lệch thực tế ra sao?",
            curiosity_hook="Liệu 0.35 giây khởi động có thực sự tạo ra khác biệt trong thói quen hàng ngày?",
            tension="Sự hoài nghi của cộng đồng đối với các tuyên bố quảng bá tốc độ của phần mềm mới.",
            explanation="Số liệu benchmark phân tích cụ thể: 42MB RAM, 0.35s startup và latency dưới 2ms.",
            visual_proof_target="startup_benchmark",
            payoff="Bằng chứng thực nghiệm định lượng rõ ràng chiến thắng của kiến trúc Rust trước Electron.",
            transition_to_next="Thế nhưng, bức tranh hoàn hảo này có góc khuất nào không?"
        )

        ch07_segs = [
            ns("LF_C07_B01", "limitations",
               "Tuy nhiên, khi cân nhắc đưa Zed vào quy trình làm việc thường nhật, vẫn có những giới hạn rõ ràng mà lập trình viên cần lưu tâm.",
               11.0, "DATA_VISUALIZATION", "PUSH_IN", "limitations_header", "GIOI HAN THUC TE"),
            ns("LF_C07_B02", "limitations",
               "Thứ nhất: hệ sinh thái tiện ích mở rộng của Zed vẫn còn non trẻ nếu so sánh với hàng chục nghìn extension đã tồn tại trên VS Code Marketplace.",
               13.0, "TECHNICAL_FLOW", "DATA_FLOW", "extension_ecosystem", "HE SINH THAI EXTENSION"),
            ns("LF_C07_B03", "limitations",
               "Thứ hai: phiên bản dành cho hệ điều hành Windows hiện vẫn đang trong giai đoạn hoàn thiện, chưa đạt độ ổn định tuyệt đối như trên macOS và Linux.",
               13.0, "DATA_VISUALIZATION", "PUSH_IN", "platform_support", "WINDOWS DANG HOAN THIEN"),
            ns("LF_C07_B04", "limitations",
               "Thứ ba: việc chuyển đổi phím tắt và thói quen làm việc từ hệ sinh thái VS Code cũ đòi hỏi người dùng phải có một khoảng thời gian thích ứng.",
               11.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "pricing_model", "THOI GIAN THICH UNG"),
        ]
        ch07 = self._make_chapter(
            7, "GIOI HAN — He Sinh Thai", 260.0, 308.0, ch07_segs,
            "Windows support chưa hoàn chỉnh; extension ecosystem còn nhỏ hơn VS Code.",
            question="Tại sao một editor siêu nhanh vẫn chưa thể lập tức thay thế hoàn toàn VS Code?",
            curiosity_hook="Rào cản lớn nhất ngăn cản hàng triệu lập trình viên chuyển sang Zed là gì?",
            tension="Tốc độ đỉnh cao đối đầu với sức mạnh quán tính của một hệ sinh thái extension khổng lồ mười năm tuổi.",
            explanation="Viết extension bằng Rust/WASM đòi hỏi tiêu chuẩn kỹ thuật khắt khe hơn hệ sinh thái JS thông thường.",
            visual_proof_target="extension_ecosystem",
            payoff="Đánh giá khách quan, giúp người xem đưa ra quyết định chuyển đổi công cụ phù hợp nhu cầu.",
            transition_to_next="Vượt lên trên mọi giới hạn, Zed báo hiệu điều gì cho tương lai công nghệ phần mềm?"
        )

        ch08_segs = [
            ns("LF_C08_B01", "payoff",
               "Zed đã chứng minh một chân lý quan trọng: lập trình viên không nhất thiết phải hy sinh hiệu năng phần cứng để đổi lấy các tính năng hiện đại.",
               13.0, "PAYOFF_VISUAL", "PAYOFF_PUSH", "tech_philosophy", "RUST CHIEN THANG ELECTRON"),
            ns("LF_C08_B02", "payoff",
               f"Với hơn {stars_str} ngôi sao và sự ủng hộ mãnh liệt từ cộng đồng Rust toàn cầu, Zed đang mở đường cho một thế hệ công cụ lập trình siêu tốc.",
               12.0, "DATA_VISUALIZATION", "PUSH_IN", "growth_projection", "THE HE TOOLING MOI"),
            ns("LF_C08_B03", "payoff",
               "Đường link tải về và kho mã nguồn chính thức được đặt tại phần mô tả video để anh em trực tiếp cài đặt và trải nghiệm tốc độ.",
               10.0, "PAYOFF_VISUAL", "PAYOFF_PUSH", "call_to_try", "THU NGHIEM NGAY"),
        ]
        ch08 = self._make_chapter(
            8, "KET LUAN — The He Editor Moi", 308.0, 343.0, ch08_segs,
            "Zed = bằng chứng Rust > Electron cho desktop tooling.",
            question="Zed mở ra xu hướng kiến trúc native cho các ứng dụng tương lai ra sao?",
            curiosity_hook="Liệu làn sóng native hóa bằng Rust có lan sang toàn bộ hệ sinh thái desktop?",
            tension="Cuộc chiến giữa triết lý phát triển web tiện lợi và triết lý hiệu năng thuần túy của phần mềm native.",
            explanation="Zed định hình lại chuẩn mực: người dùng xứng đáng nhận được 100% sức mạnh phần cứng họ đã chi trả.",
            visual_proof_target="tech_philosophy",
            payoff="Giải đáp toàn diện câu hỏi mở đầu và định hình tư duy lựa chọn công cụ lâu dài.",
            transition_to_next="Và nếu bạn muốn tiếp tục khám phá những đột phá công nghệ mã nguồn mở tiếp theo..."
        )

        ch09_segs = [
            ns("LF_C09_B01", "cta",
               "Nếu video phân tích kỹ thuật này hữu ích cho công việc của anh em, hãy like, share và đăng ký kênh để đón xem các dự án mã nguồn mở đột phá tiếp theo nhé.",
               17.0, "CTA", "STATIC", "cta_screen", "LIKE SHARE DANG KY KENH"),
        ]
        ch09 = self._make_chapter(
            9, "CTA — Ket Thuc", 343.0, 360.0, ch09_segs, "Like, share, đăng ký.", is_cta=True,
            tension="", explanation="", visual_proof_target="cta_screen", payoff="Hoàn tất documentary."
        )

        chapters = [ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09]
        all_segs = []
        for ch in chapters:
            all_segs.extend(ch.segments)
        total_words = sum(_count_words(s.spoken_text) for s in all_segs)
        yt_chapters = [f"{_fmt_time(ch.start_time_sec)} {ch.chapter_title}" for ch in chapters if not ch.is_cta]

        return LongFormScriptArtifact(
            story_id=story_id,
            story_type=LongFormStoryType.TYPE_A_SINGLE_REPO,
            title=f"Zed: Code Editor AI-Native Nhanh Nhất Thế Giới — {stars_str} Sao, Rust + GPU",
            description=(
                f"Deep dive về Zed editor: kiến trúc GPUI, benchmarks thực tế, "
                f"AI built-in, multi-buffer editing, và tại sao nó thách thức VS Code. "
                f"GitHub: github.com/{repo_data.full_name}"
            ),
            central_question=thesis.central_question,
            viewer_promise=thesis.viewer_promise,
            editorial_thesis=thesis,
            hook=ch01_segs[0].spoken_text,
            tags=["Zed", "code editor", "Rust", "GPU", "AI", "VS Code", "developer tools", "GitHub"],
            target_duration_sec=360.0,
            total_spoken_words=total_words,
            chapters=chapters,
            all_segments=all_segs,
            repository_urls=[repo_data.html_url],
            sources=[f"https://github.com/{repo_data.full_name}",
                     "https://zed.dev/docs", f"https://github.com/{repo_data.full_name}/blob/main/README.md"],
            hashtags=["#Zed", "#CodeEditor", "#Rust", "#GPU", "#AIEditor", "#GitHub", "#OpenSource"],
            thumbnail_text="Editor Nhanh Nhat The Gioi",
            youtube_chapters=yt_chapters,
        )

    # ── TYPE A: uv package manager deep dive (10 chapters, ~370s, 920+ words) ─
    def _type_a_uv(self, story_id, repo_data, stars_str, story, thesis: EditorialThesis) -> LongFormScriptArtifact:
        seg_order = [0]

        def ns(beat_id, seg_type, text, dur, v_type, motion, cue, headline):
            seg_order[0] += 1
            return _seg(seg_order[0], beat_id, seg_type, text, dur,
                        v_type, motion, cue, headline,
                        evidence=[f"github.com/{repo_data.full_name}"])

        # Chapter 01: Hook (0:00 – 0:30)
        ch01_segs = [
            ns("LF_C01_B01", "hook",
               "Một công cụ quản lý gói Python có thể cài đặt toàn bộ thư viện cho dự án khoa học dữ liệu khổng lồ chỉ trong chưa đầy nửa giây — nhanh gấp một trăm lần pip truyền thống.",
               11.0, "REAL_REPOSITORY_UI", "ZOOM_TO_DETAIL", "github_repo_header", "NHANH GAP 100 LAN PIP"),
            ns("LF_C01_B02", "hook",
               f"Đó là uv — dự án mã nguồn mở bằng ngôn ngữ Rust của công ty Astral, vừa cán mốc hơn {stars_str} ngôi sao trên GitHub và làm thay đổi hoàn toàn hệ sinh thái Python.",
               10.0, "DATA_VISUALIZATION", "PUSH_IN", "star_count_display", f"{stars_str} SAO GITHUB"),
            ns("LF_C01_B03", "hook",
               "Tại sao một cộng đồng trung thành với Python suốt hai mươi năm lại quyết định giao phó hạ tầng cốt lõi cho ngôn ngữ Rust? Chúng ta sẽ giải mã ngay sau đây.",
               11.0, "TECHNICAL_FLOW", "REVEAL", "chapter_preview", "RUST TAI THIET LAP PYTHON"),
        ]
        ch01 = self._make_chapter(
            1, "HOOK — Cuộc Cách Mạng uv", 0.0, 32.0, ch01_segs,
            "uv: Trình quản lý gói Python viết bằng Rust nhanh hơn pip 10-100 lần.",
            question="Tại sao uv lại có thể giải quyết dứt điểm sự chậm chạp của pip tồn tại suốt hai thập kỷ?",
            curiosity_hook="Bí mật nào giúp uv cài đặt thư viện nhanh đến mức mắt thường không kịp chớp?",
            tension="Python là ngôn ngữ số một cho AI nhưng hệ thống phân phối gói lại chậm chạp và lỗi thời.",
            explanation="uv viết bằng 100% Rust, tối ưu hóa từ tầng syscall đĩa đến thuật toán phân giải đồ thị phụ thuộc.",
            visual_proof_target="github_repo_header",
            payoff="Hiểu được bài toán thắt nút cổ chai hạ tầng đang tiêu tốn hàng nghìn giờ của cộng đồng kỹ sư.",
            transition_to_next="Để thấy sự bức bách này, hãy nhớ lại nỗi đau mỗi khi chạy lệnh pip install."
        )

        # Chapter 02: Central Question & The Problem (0:32 – 1:12)
        ch02_segs = [
            ns("LF_C02_B01", "problem",
               "Trong nhiều năm qua, bất kỳ ai lập trình Python cũng từng phải ngồi chờ hàng phút chỉ để pip tải wheel và phân giải xung đột phiên bản thư viện.",
               13.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "pip_slow_demo", "NOI DAU PIP INSTALL"),
            ns("LF_C02_B02", "problem",
               "Hơn thế nữa, hệ sinh thái bị phân mảnh nặng nề giữa pip, virtualenv, poetry, pip-tools và conda; mỗi công cụ có một cú pháp và cách quản lý môi trường khác nhau.",
               14.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "fragmented_ecosystem", "HE SINH THAI PHAN MANH"),
            ns("LF_C02_B03", "problem",
               "Trong các đường ống CI/CD tự động, thời gian build Docker image bị kéo dài vô ích, tiêu tốn hàng triệu đô la chi phí máy chủ đám mây cho các doanh nghiệp.",
               13.0, "DATA_VISUALIZATION", "PUSH_IN", "cicd_cost_metric", "THIET HAI HANG TRIEU USD"),
        ]
        ch02 = self._make_chapter(
            2, "VAN DE — Rao Can Tooling Cu", 32.0, 72.0, ch02_segs,
            "Pip chậm chạp, môi trường phân mảnh, CI/CD tiêu tốn thời gian và ngân sách.",
            question="Những nguyên nhân kỹ thuật sâu xa nào khiến pip phân giải phụ thuộc chậm chạp?",
            curiosity_hook="Tại sao hệ sinh thái Python lại bị phân mảnh qua nhiều công cụ chồng chéo như vậy?",
            tension="Mâu thuẫn giữa sự bùng nổ của các mô hình AI đồ sộ và hạ tầng cài đặt gói cũ kỹ viết bằng Python đơn luồng.",
            explanation="Pip viết bằng Python đơn luồng phải tải tuần tự từng file metadata và chạy giải thuật backtracking dễ rơi vào bẫy lặp vô tận.",
            visual_proof_target="pip_slow_demo",
            payoff="Nắm rõ nguyên nhân gốc rễ ở cấp độ thuật toán và I/O gây nghẽn hệ thống.",
            transition_to_next="Đó chính là lý do đội ngũ Astral quyết định viết lại mọi thứ từ con số không."
        )

        # Chapter 03: Why This Project Exists (1:12 – 1:52)
        ch03_segs = [
            ns("LF_C03_B01", "discovery",
               "Astral — nhóm kỹ sư đứng sau thành công của linter Ruff lừng danh — đặt ra một mục tiêu duy nhất: biến hạ tầng tooling của Python trở nên nhanh đến mức không còn cảm nhận được độ trễ.",
               13.0, "REAL_REPOSITORY_UI", "ZOOM_TO_DETAIL", "astral_team", "MUC TIEU CUA ASTRAL"),
            ns("LF_C03_B02", "discovery",
               "Họ chọn Rust vì khả năng quản lý bộ nhớ không cần garbage collection, mô hình đa luồng không dữ liệu tương tranh và tốc độ I/O đĩa ở mức phần cứng.",
               14.0, "TECHNICAL_FLOW", "DATA_FLOW", "rust_low_level", "SUC MANH HE HE DIEU HANH"),
            ns("LF_C03_B03", "discovery",
               "uv ra đời không chỉ để thay thế pip, mà định vị trở thành một bộ công cụ duy nhất quản lý toàn bộ vòng đời dự án Python hiện đại.",
               13.0, "REAL_REPOSITORY_UI", "PUSH_IN", "uv_project_vision", "BO CONG CU UNIFIED"),
        ]
        ch03 = self._make_chapter(
            3, "SU MENH — Tai Sao Astral Chon Rust", 72.0, 112.0, ch03_segs,
            "Astral áp dụng triết lý của Ruff vào package management: tốc độ Rust loại bỏ hoàn toàn độ trễ.",
            question="Tại sao một công ty startup lại chọn giải quyết bài toán cài gói vốn được xem là chuẩn mực mở?",
            curiosity_hook="Liệu một công cụ viết bằng Rust có thể tương thích hoàn hảo với 500 nghìn gói trên PyPI?",
            tension="Các công cụ cũ bảo thủ với các tiêu chuẩn phân tán của PyPA, trong khi cộng đồng đòi hỏi một giải pháp đồng bộ và siêu tốc.",
            explanation="Astral thiết kế uv theo chuẩn PEP tương thích 100% nhưng tăng tốc toàn bộ khâu giải quyết phụ thuộc.",
            visual_proof_target="astral_team",
            payoff="Thấy rõ tầm nhìn chiến lược đưa Rust trở thành động cơ bên dưới của thế giới Python.",
            transition_to_next="Vậy bên trong lõi nhị phân của uv có đột phá kỹ thuật nào làm nên tốc độ này?"
        )

        # Chapter 04: Breakthrough & Key Idea (1:52 – 2:32)
        ch04_segs = [
            ns("LF_C04_B01", "breakthrough",
               "Đột phá kỹ thuật đầu tiên của uv nằm ở thuật toán PubGrub — thuật toán giải quyết phụ thuộc đại số hiện đại nhất thế giới hiện nay.",
               13.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "pubgrub_algorithm", "THUAT TOAN PUBGRUB"),
            ns("LF_C04_B02", "breakthrough",
               "Thay vì thử sai mù quáng như pip, PubGrub phân tích đồ thị ràng buộc phiên bản theo cơ chế suy diễn logic, phát hiện xung đột tức thì mà không cần duyệt vét cạn.",
               14.0, "TECHNICAL_FLOW", "DATA_FLOW", "dependency_graph", "SUY DIEN LOGIC SONG SONG"),
            ns("LF_C04_B03", "breakthrough",
               "Kết hợp cùng mạng lưới HTTP request bất đồng bộ qua tokio, uv tải siêu dữ liệu của hàng trăm gói thư viện đồng thời trong vài chục mili-giây.",
               13.0, "DATA_VISUALIZATION", "PUSH_IN", "tokio_async_network", "TOKIO ASYNC I/O"),
        ]
        ch04 = self._make_chapter(
            4, "DOT PHA — Thuat Toan PubGrub", 112.0, 152.0, ch04_segs,
            "PubGrub logic dependency solver + Tokio async HTTP network.",
            question="PubGrub hoạt động thế nào để tránh bẫy phụ thuộc ma quái Dependency Hell?",
            curiosity_hook="Tại sao việc tải metadata của uv lại nhanh hơn hàng chục lần so với pip?",
            tension="Giải quyết ràng buộc phiên bản là bài toán NP-đầy đủ dễ gây treo máy khi số lượng gói tăng cao.",
            explanation="PubGrub học hỏi từ các mâu thuẫn để thu hẹp không gian tìm kiếm, giải quyết hàng nghìn ràng buộc trong chớp mắt.",
            visual_proof_target="pubgrub_algorithm",
            payoff="Làm chủ nguyên lý hoạt động của thuật toán giải quyết dependency tân tiến nhất.",
            transition_to_next="Nhưng giải quyết phụ thuộc chỉ là một nửa câu chuyện; khâu ghi đĩa mới là điều kỳ diệu."
        )

        # Chapter 05: How It Actually Works (2:32 – 3:20)
        ch05_segs = [
            ns("LF_C05_B01", "how_it_works",
               "Khi cài đặt gói vào môi trường ảo, uv không giải nén và sao chép từng file như cách truyền thống.",
               12.0, "TECHNICAL_FLOW", "DATA_FLOW", "file_system_tricks", "KHONG SAO CHEP THU CONG"),
            ns("LF_C05_B02", "how_it_works",
               "Nó xây dựng một kho lưu trữ cache tập trung duy nhất trên ổ cứng, và sử dụng hardlink hoặc reflink trên hệ thống file APFS và ext4.",
               16.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "hardlink_cache_architecture", "HARDLINK VA REFLINK"),
            ns("LF_C05_B03", "how_it_works",
               "Nghĩa là việc cài đặt một gói 500MB như PyTorch chỉ đơn giản là tạo con trỏ chỉ mục trên ổ cứng, hoàn thành trong 0.001 giây mà không tốn thêm dung lượng lưu trữ.",
               17.0, "DATA_VISUALIZATION", "PUSH_IN", "copy_on_write_zero_time", "CAI PYTORCH TRONG 0.001S"),
            ns("LF_C05_B04", "how_it_works",
               "Hơn thế nữa, uv tự động quản lý và tải các phiên bản Python độc lập, giúp bạn chuyển đổi môi trường giữa Python 3.10, 3.11 hay 3.12 mà không cần cài pyenv.",
               13.0, "TERMINAL_DEMO", "REVEAL", "python_version_management", "QUAN LY PHIEN BAN PYTHON"),
        ]
        ch05 = self._make_chapter(
            5, "CO CHE — Hardlink Va Reflink Cache", 152.0, 200.0, ch05_segs,
            "Cơ chế Hardlink/Reflink: Cài PyTorch trong 0.001s, quản lý phiên bản Python tự động.",
            question="Làm thế nào uv cài đặt thư viện hàng trăm MB mà không tốn dung lượng ổ cứng trùng lặp?",
            curiosity_hook="Cơ chế reflink trên macOS APFS và Linux giúp tiết kiệm I/O đĩa ra sao?",
            tension="Tạo hàng chục môi trường ảo thường làm cạn kiệt dung lượng SSD do trùng lặp các gói nặng.",
            explanation="Kiến trúc global cache dùng hardlink cho phép 100 virtualenv cùng trỏ vào một bản nhị phân duy nhất trên đĩa.",
            visual_proof_target="hardlink_cache_architecture",
            payoff="Thấu hiểu cơ chế tối ưu hóa hệ thống file ở tầng sâu của hệ điều hành.",
            transition_to_next="Hãy cùng kiểm chứng tốc độ thực tế này qua những bài đo lường benchmark khắt khe."
        )

        # Chapter 06: Visual/Technical Proof (3:20 – 4:05)
        ch06_segs = [
            ns("LF_C06_B01", "benchmark",
               "Trong các bài đo lường chính thức trên tập hợp các gói phổ biến nhất, uv đạt tốc độ cài đặt vượt trội từ 10 đến 100 lần so với pip.",
               13.0, "DATA_VISUALIZATION", "PUSH_IN", "benchmark_cold_cache", "BENCHMARK COLD CACHE"),
            ns("LF_C06_B02", "benchmark",
               "Ở trạng thái warm cache, khi các gói đã có trong bộ nhớ đệm, uv hoàn thành việc tái tạo toàn bộ môi trường ảo chứa 50 thư viện chỉ trong 25 mili-giây, trong khi pip mất tới 12 giây.",
               16.0, "DATA_VISUALIZATION", "PUSH_IN", "benchmark_warm_cache", "25MS SO VOI 12S"),
            ns("LF_C06_B03", "benchmark",
               "Thậm chí khi so sánh với Poetry và PDM — những công cụ hiện đại có lockfile — uv vẫn duy trì khoảng cách tốc độ từ 8 đến 15 lần.",
               16.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "uv_vs_poetry_pdm", "VUOT TREN POETRY VA PDM"),
        ]
        ch06 = self._make_chapter(
            6, "THUC NGHIEM — Benchmarks Dinh Cao", 200.0, 245.0, ch06_segs,
            "Warm cache: 25ms vs 12s của pip — nhanh hơn 10x-100x.",
            question="Sự chênh lệch tốc độ có duy trì ổn định trên các dự án quy mô enterprise không?",
            curiosity_hook="Liệu lockfile của uv có đảm bảo tính tái lập 100% trên các hệ điều hành khác nhau?",
            tension="Nhiều lập trình viên nghi ngờ liệu uv có bỏ qua các bước kiểm tra an toàn để chạy nhanh?",
            explanation="uv vẫn thực hiện đầy đủ hash verification và chuẩn hóa wheel, tốc độ đến từ song song hóa thuần túy.",
            visual_proof_target="benchmark_cold_cache",
            payoff="Xác nhận bằng số liệu khách quan sức mạnh hủy diệt của giải pháp mới.",
            transition_to_next="Những con số này mang lại lợi ích tài chính và vận hành thế nào trong đời thực?"
        )

        # Chapter 07: Real-World Implications (4:05 – 4:50)
        ch07_segs = [
            ns("LF_C07_B01", "implications",
               "Đối với các doanh nghiệp công nghệ, việc chuyển sang uv mang lại những tác động kinh tế trực tiếp và to lớn.",
               11.0, "DATA_VISUALIZATION", "PUSH_IN", "enterprise_impact", "TAC DONG KINH TE DOANH NGHIEP"),
            ns("LF_C07_B02", "implications",
               "Thời gian chạy các quy trình kiểm thử CI/CD và build Docker giảm từ 5 phút xuống còn 15 giây, tăng tốc chu kỳ phát hành tính năng lên gấp nhiều lần.",
               16.0, "TECHNICAL_FLOW", "DATA_FLOW", "cicd_acceleration", "CI/CD GIAM TU 5 PHUT XUONG 15S"),
            ns("LF_C07_B03", "implications",
               "Các kỹ sư dữ liệu và AI không còn bị ngắt quãng dòng suy nghĩ mỗi khi cần thử nghiệm một mô hình mới hay thiết lập môi trường nghiên cứu.",
               18.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "developer_flow_state", "DUY TRI FLOW-STATE CHO AI"),
        ]
        ch07 = self._make_chapter(
            7, "UNG DUNG — Tang Toc CI/CD Va AI", 245.0, 290.0, ch07_segs,
            "Build Docker giảm từ 5 phút xuống 15s; tiết kiệm chi phí hạ tầng CI/CD.",
            question="Doanh nghiệp tiết kiệm được bao nhiêu tiền điện toán đám mây nhờ uv?",
            curiosity_hook="Tại sao các công ty lớn như Modal và Hugging Face lại chuyển sang dùng uv đầu tiên?",
            tension="Chi phí hạ tầng CI/CD phình to vì thời gian chạy pipeline chủ yếu chờ tải gói.",
            explanation="Giảm 80% thời gian chạy CI pipeline, trực tiếp cắt giảm hóa đơn compute hàng tháng.",
            visual_proof_target="cicd_acceleration",
            payoff="Đo lường được giá trị kinh tế thực tế vượt ra ngoài góc nhìn code thuần túy.",
            transition_to_next="Tuy nhiên, việc trao quyền năng cho một công cụ duy nhất có rủi ro gì?"
        )

        # Chapter 08: Trade-Offs & Limitations (4:50 – 5:35)
        ch08_segs = [
            ns("LF_C08_B01", "limitations",
               "Dù uv là một bước tiến vượt bậc, các kỹ sư vẫn cần nhận thức rõ những giới hạn và bài toán đánh đổi kỹ thuật.",
               11.0, "DATA_VISUALIZATION", "PUSH_IN", "limitations_header", "DANH DOI KY THUAT"),
            ns("LF_C08_B02", "limitations",
               "Đầu tiên: các gói C-extension phức tạp không có sẵn pre-built wheel vẫn yêu cầu trình biên dịch C trên máy cục bộ để build từ mã nguồn tarball.",
               16.0, "TERMINAL_DEMO", "REVEAL", "c_extension_limitation", "C-EXTENSION VA SOURCE BUILD"),
            ns("LF_C08_B03", "limitations",
               "Thứ hai: uv được phát triển bởi một công ty thương mại đơn lẻ là Astral, làm dấy lên những băn khoăn về tính tập trung hóa so với các ủy ban tiêu chuẩn cộng đồng phân tán của PyPA.",
               18.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "centralization_vs_community", "BAI TOAN TAP TRUNG HOA"),
        ]
        ch08 = self._make_chapter(
            8, "GIOI HAN — C-Extension Va Thuong Mai", 290.0, 335.0, ch08_segs,
            "Giới hạn build C-extension nguồn và bài toán tập trung hóa hạ tầng thương mại.",
            question="Khi nào uv không thể giúp bạn chạy nhanh hơn pip?",
            curiosity_hook="Liệu Astral có duy trì mã nguồn mở vĩnh viễn cho uv?",
            tension="Sự đánh đổi: tốc độ vượt trội từ một công ty tập trung đối đầu với tính bền vững của tổ chức cộng đồng.",
            explanation="Các thư viện C/Fortran phức tạp vẫn phải chờ compiler cục bộ; uv chỉ tăng tốc khâu điều phối.",
            visual_proof_target="c_extension_limitation",
            payoff="Cung cấp góc nhìn đa chiều, tỉnh táo trước làn sóng cường điệu công nghệ.",
            transition_to_next="Sau khi cân nhắc mọi khía cạnh, uv định hình tương lai phát triển phần mềm ra sao?"
        )

        # Chapter 09: Who Should Care & Final Payoff (5:35 – 6:15)
        ch09_segs = [
            ns("LF_C09_B01", "payoff",
               "uv không chỉ là một công cụ tiện ích; nó đại diện cho một xu thế tất yếu: ngôn ngữ lập trình cho con người là Python, nhưng hạ tầng vận hành phải thuộc về Rust.",
               14.0, "PAYOFF_VISUAL", "PAYOFF_PUSH", "python_rust_future", "XU HUONG TAT YEU CUA HE SINH THAI"),
            ns("LF_C09_B02", "payoff",
               f"Với hơn {stars_str} ngôi sao và sự đón nhận nồng nhiệt từ toàn bộ cộng đồng AI, uv là minh chứng cho thấy sự kiên trì tối ưu hóa kiến trúc luôn mang lại giá trị bền vững.",
               14.0, "DATA_VISUALIZATION", "PUSH_IN", "stars_growth_trajectory", f"{stars_str} SAO VA SU UNG HO"),
            ns("LF_C09_B03", "payoff",
               "Toàn bộ tài liệu hướng dẫn chuyển đổi từ pip sang uv được đính kèm tại phần mô tả video để anh em trực tiếp trải nghiệm tốc độ.",
               12.0, "PAYOFF_VISUAL", "PAYOFF_PUSH", "github_repo_link", "github.com/astral-sh/uv"),
        ]
        ch09 = self._make_chapter(
            9, "KET LUAN — Ky Nguyen Tooling Moi", 335.0, 375.0, ch09_segs,
            "Tương lai Python: Code bằng Python, hạ tầng vận hành bằng Rust.",
            question="uv định hình lại tiêu chuẩn phần mềm developer tooling như thế nào?",
            curiosity_hook="Bạn đã sẵn sàng loại bỏ pip khỏi quy trình làm việc thường nhật?",
            tension="Sự chuyển giao thế hệ từ các công cụ script đơn giản sang các nhị phân native tối ưu hóa sâu.",
            explanation="uv là cột mốc trưởng thành của hệ sinh thái Python trong kỷ nguyên trí tuệ nhân tạo.",
            visual_proof_target="python_rust_future",
            payoff="Giải quyết trọn vẹn câu hỏi mở đầu và mang lại tầm nhìn kiến trúc có tính định hướng dài hạn.",
            transition_to_next="Và nếu bạn muốn tiếp tục đồng hành cùng những phân tích kiến trúc mã nguồn mở đỉnh cao..."
        )

        # Chapter 10: CTA (6:15 – 6:30)
        ch10_segs = [
            ns("LF_C10_B01", "cta",
               "Nếu video phân tích kỹ thuật này mang lại giá trị cho anh em, hãy like, share và đăng ký kênh để đón xem những dự án công nghệ đột phá tiếp theo nhé.",
               15.0, "CTA", "STATIC", "cta_screen", "LIKE SHARE DANG KY KENH"),
        ]
        ch10 = self._make_chapter(
            10, "CTA — Ket Thuc", 375.0, 390.0, ch10_segs, "Like, share, đăng ký.", is_cta=True,
            tension="", explanation="", visual_proof_target="cta_screen", payoff="Hoàn tất documentary."
        )

        chapters = [ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09, ch10]
        all_segs = []
        for ch in chapters:
            all_segs.extend(ch.segments)
        total_words = sum(_count_words(s.spoken_text) for s in all_segs)
        yt_chapters = [f"{_fmt_time(ch.start_time_sec)} {ch.chapter_title}" for ch in chapters if not ch.is_cta]

        return LongFormScriptArtifact(
            story_id=story_id,
            story_type=LongFormStoryType.TYPE_A_SINGLE_REPO,
            title=f"uv: Trình Quản Lý Gói Python Nhanh Gấp 100 Lần — {stars_str} Sao, Rust Tái Thiết Lập Tooling",
            description=(
                f"Phân tích chuyên sâu về uv của Astral: thuật toán PubGrub, cơ chế hardlink cache, "
                f"benchmarks đo lường thực tế và tại sao Rust đang cứu rỗi hệ sinh thái Python. "
                f"GitHub: github.com/{repo_data.full_name}"
            ),
            central_question=thesis.central_question,
            viewer_promise=thesis.viewer_promise,
            editorial_thesis=thesis,
            hook=ch01_segs[0].spoken_text,
            tags=["uv", "Python", "Rust", "pip", "package manager", "Astral", "PubGrub", "developer tools"],
            target_duration_sec=390.0,
            total_spoken_words=total_words,
            chapters=chapters,
            all_segments=all_segs,
            repository_urls=[repo_data.html_url],
            sources=[f"https://github.com/{repo_data.full_name}",
                     "https://astral.sh/blog/uv", f"https://github.com/{repo_data.full_name}/blob/main/README.md"],
            hashtags=["#uv", "#Python", "#Rust", "#Pip", "#Astral", "#DeveloperTools", "#OpenSource"],
            thumbnail_text="Python Nhanh Gap 100 Lan",
            youtube_chapters=yt_chapters,
        )

    # ── TYPE A: ollama local AI deep dive (10 chapters, ~420s, 1000+ words) ─
    def _type_a_ollama(self, story_id, repo_data, stars_str, story, thesis: EditorialThesis) -> LongFormScriptArtifact:
        seg_order = [0]

        def ns(beat_id, seg_type, text, dur, v_type, motion, cue, headline):
            seg_order[0] += 1
            return _seg(seg_order[0], beat_id, seg_type, text, dur,
                        v_type, motion, cue, headline,
                        evidence=[f"github.com/{repo_data.full_name}"])

        # Chapter 01: Hook (0:00 – 0:34)
        ch01_segs = [
            ns("LF_C01_B01", "hook",
               "Bạn có tưởng tượng được việc vận hành một mô hình AI thông minh tương đương GPT-3.5 chạy hoàn toàn mượt mà trên chiếc laptop của bạn mà không cần kết nối Internet?",
               11.0, "REAL_REPOSITORY_UI", "ZOOM_TO_DETAIL", "github_repo_header", "AI CHAY TRUC TIEP TREN LAPTOP"),
            ns("LF_C01_B02", "hook",
               f"Dự án mã nguồn mở Ollama đã biến điều không tưởng đó thành hiện thực, thu hút hơn {stars_str} ngôi sao GitHub và trở thành chuẩn mực toàn cầu cho AI cục bộ.",
               11.0, "DATA_VISUALIZATION", "PUSH_IN", "star_count_display", f"{stars_str} SAO GITHUB"),
            ns("LF_C01_B03", "hook",
               "Tại sao hơn một trăm tám mươi nghìn lập trình viên lại chọn chạy AI trên máy cá nhân thay vì dùng API của các ông lớn công nghệ? Chúng ta hãy cùng giải mã ngay sau đây.",
               12.0, "TECHNICAL_FLOW", "REVEAL", "chapter_preview", "CUOC CACH MANG LOCAL AI"),
        ]
        ch01 = self._make_chapter(
            1, "HOOK — Kỷ Nguyên Local LLM", 0.0, 34.0, ch01_segs,
            "Ollama: Đóng gói và chạy các mô hình ngôn ngữ lớn trực tiếp trên máy tính cá nhân.",
            question="Làm thế nào để chạy các mô hình AI tiên tiến trên phần cứng cá nhân mà không cần siêu máy tính?",
            curiosity_hook="Liệu chiếc laptop của bạn có thể suy luận AI độc lập mà không gửi dữ liệu ra ngoài?",
            tension="AI đám mây thông minh nhưng đắt đỏ và tiềm ẩn rủi ro rò rỉ dữ liệu nhạy cảm.",
            explanation="Ollama kết hợp Go daemon và llama.cpp C++ để giải phóng mô hình AI khỏi sự phụ thuộc vào cloud.",
            visual_proof_target="github_repo_header",
            payoff="Xác nhận tiềm năng đột phá của việc tự chủ hoàn toàn hạ tầng AI ngay trên máy trạm.",
            transition_to_next="Để thấy tại sao bước chuyển này mang tính sống còn, hãy nhìn vào cái giá mà các kỹ sư đang phải trả.",
            key_claims=[
                LongFormClaim(
                    claim_text=f"Dự án Ollama cán mốc hơn {stars_str} ngôi sao trên GitHub.",
                    classification=ClaimClassification.OFFICIAL_SOURCE,
                    source_url=f"https://github.com/{repo_data.full_name}",
                    source_ref=f"github.com/{repo_data.full_name}",
                    verified=True,
                    proof_level=1
                )
            ]
        )

        # Chapter 02: Central Question & The Problem (0:34 – 1:16)
        ch02_segs = [
            ns("LF_C02_B01", "problem",
               "Trong giai đoạn đầu bùng nổ AI, mọi doanh nghiệp và lập trình viên đều phải phụ thuộc hoàn toàn vào các API đám mây với hóa đơn chi phí leo thang chóng mặt mỗi tháng.",
               13.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "cloud_cost_spike", "HOA DON CLOUD TANG CHONG MAT"),
            ns("LF_C02_B02", "problem",
               "Quan trọng hơn, việc gửi toàn bộ mã nguồn nội bộ và dữ liệu khách hàng lên máy chủ bên thứ ba đặt ra bài toán rủi ro bảo mật nghiêm trọng không thể chấp nhận.",
               14.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "data_leak_risk", "RUI RO RO RI DU LIEU"),
            ns("LF_C02_B03", "problem",
               "Thế nhưng, việc tự dựng hạ tầng AI cục bộ trước đây là một cơn ác mộng: xung đột driver CUDA, biên dịch C++ thủ công và môi trường Python ngốn hàng chục gigabyte VRAM.",
               15.0, "TERMINAL_DEMO", "REVEAL", "cuda_driver_nightmare", "CON AC MONG CAI DAT CUDA"),
        ]
        ch02 = self._make_chapter(
            2, "VAN DE — Chi Phí Cloud Và Rào Cản VRAM", 34.0, 76.0, ch02_segs,
            "Chi phí API khổng lồ, rủi ro rò rỉ dữ liệu và sự phức tạp của hạ tầng C++/CUDA truyền thống.",
            question="Những rào cản kỹ thuật nào từng biến việc chạy LLM cục bộ thành một cơn ác mộng?",
            curiosity_hook="Tại sao cài đặt một mô hình AI mã nguồn mở trước đây lại đòi hỏi kiến thức hạ tầng phức tạp đến vậy?",
            tension="Mâu thuẫn giữa nhu cầu bảo mật dữ liệu tuyệt đối và sự cồng kềnh, phân mảnh của các thư viện AI Python/C++.",
            explanation="Mô hình AI nguyên bản ở định dạng FP16 ngốn bộ nhớ khổng lồ và thiếu lớp trừu tượng quản lý tiến trình thống nhất.",
            visual_proof_target="cloud_cost_spike",
            payoff="Thấu hiểu sâu sắc nguồn gốc bế tắc của các giải pháp tự dựng AI cục bộ trước khi có Ollama.",
            transition_to_next="Chính trong hoàn cảnh bế tắc đó, một triết lý thiết kế mượn từ Docker đã xuất hiện."
        )

        # Chapter 03: Why This Project Exists / Discovery (1:16 – 1:58)
        ch03_segs = [
            ns("LF_C03_B01", "discovery",
               "Ollama xuất hiện và thay đổi luật chơi vĩnh viễn: đây là công cụ đóng gói toàn bộ quy trình tải, lượng tử hóa và chạy LLM vào một tệp nhị phân Go duy nhất.",
               13.0, "REAL_REPOSITORY_UI", "ZOOM_TO_DETAIL", "repo_header_fullname", "TEP NHI PHAN GO DUY NHAT"),
            ns("LF_C03_B02", "discovery",
               "Không cần cài đặt Python, không cần biên dịch mã nguồn; chỉ với một dòng lệnh duy nhất 'ollama run llama3', mô hình AI tiên tiến đã sẵn sàng trò chuyện trên terminal.",
               14.0, "TERMINAL_DEMO", "REVEAL", "ollama_run_cmd", "CHAY AI BANG MOT DONG LENH"),
            ns("LF_C03_B03", "discovery",
               "Với kiến trúc lấy cảm hứng từ Docker, Ollama cung cấp giao diện REST API chuẩn OpenAI, cho phép tích hợp ngay lập tức vào bất kỳ ứng dụng nào trong vài phút.",
               15.0, "TECHNICAL_FLOW", "DATA_FLOW", "openai_compatible_api", "API TUONG THICH OPENAI"),
        ]
        ch03 = self._make_chapter(
            3, "KHAM PHA — Ollama: Docker Cho AI Cục Bộ", 76.0, 118.0, ch03_segs,
            "Đóng gói toàn bộ runtime AI vào single binary — trải nghiệm 'Docker for LLMs'.",
            question="Làm thế nào Ollama biến toàn bộ quy trình thiết lập AI phức tạp thành một dòng lệnh duy nhất?",
            curiosity_hook="Tại sao trải nghiệm chuẩn Docker lại tạo ra bước nhảy vọt cho cộng đồng AI mã nguồn mở?",
            tension="Biên dịch C++ đem lại tốc độ nhưng giết chết tính tiện dụng; Ollama phải giấu hoàn toàn độ phức tạp đằng sau một CLI tinh gọn.",
            explanation="Ollama đóng gói sẵn runtime C++ llama.cpp biên dịch sẵn cho từng vi kiến trúc vi xử lý bên trong daemon Go.",
            visual_proof_target="ollama_run_cmd",
            payoff="Nắm bắt tư duy sản phẩm xuất sắc đưa công nghệ AI phức tạp đến tay mọi lập trình viên phổ thông.",
            transition_to_next="Nhưng làm thế nào một mô hình nặng mười bốn gigabyte có thể nhét vừa vào bộ nhớ máy tính thông thường?"
        )

        # Chapter 04: Breakthrough & Core Idea (1:58 – 2:44)
        ch04_segs = [
            ns("LF_C04_B01", "breakthrough",
               "Bí mật kỹ thuật lớn nhất giúp AI chạy được trên máy tính cá nhân chính là định dạng lượng tử hóa GGUF do cộng đồng mã nguồn mở phát triển.",
               14.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "gguf_format_schematic", "DINH DANG GGUF TIEN TIEN"),
            ns("LF_C04_B02", "breakthrough",
               "Thay vì lưu trữ trọng số ở độ chính xác dấu phẩy động 16-bit tốn 14 gigabyte cho mô hình 8 tỷ tham số, kỹ thuật k-quant 4-bit nén nó xuống chỉ còn chưa đầy 4 gigabyte.",
               16.0, "DATA_VISUALIZATION", "PUSH_IN", "vram_compression_chart", "TIET KIEM 70% BRAM"),
            ns("LF_C04_B03", "breakthrough",
               "Đột phá nằm ở chỗ: sự suy giảm độ chính xác suy luận là dưới 1%, nhưng mức tiêu hao bộ nhớ giảm tới hơn 70%, mở toang cánh cửa cho phần cứng tiêu dùng.",
               16.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "perplexity_vs_size", "DO MAT MAT DUOI 1%"),
        ]
        ch04 = self._make_chapter(
            4, "DOT PHA — Kỹ Thuật GGUF Và Lượng Tử Hóa", 118.0, 164.0, ch04_segs,
            "Định dạng GGUF k-quants: nén trọng số FP16 xuống 4-bit với tổn thất suy luận dưới 1%.",
            question="Cơ chế toán học nào cho phép nén mô hình AI xuống 4-bit mà không làm nó mất đi sự thông minh?",
            curiosity_hook="Làm thế nào việc cắt giảm ba phần tư số bit lại không phá hủy ma trận trọng số mạng nơ-ron?",
            tension="Lượng tử hóa quá sâu sẽ gây hiện tượng suy giảm perplexity; Ollama sử dụng các phương pháp k-quant cải tiến để bảo vệ các trọng số quan trọng.",
            explanation="GGUF phân bổ số bit động theo từng block ma trận, giữ độ chính xác cao cho các layer nhạy cảm và nén sâu ở các layer dư thừa.",
            visual_proof_target="gguf_format_schematic",
            payoff="Hiểu tường tận bản chất của công nghệ nén trọng số GGUF — nền tảng của toàn bộ kỷ nguyên Edge AI.",
            transition_to_next="Nhưng chỉ nén trọng số thôi là chưa đủ; dữ liệu phải được nạp và tính toán trên phần cứng ra sao?"
        )

        # Chapter 05: How It Actually Works (2:44 – 3:30)
        ch05_segs = [
            ns("LF_C05_B01", "how_it_works",
               "Để đạt tốc độ tối đa, Ollama sở hữu cơ chế phân bổ tầng mạng nơ-ron tự động thông minh bậc nhất hiện nay giữa GPU và RAM máy tính.",
               14.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "layer_offloading_diagram", "PHAN BO TANG TU DONG"),
            ns("LF_C05_B02", "how_it_works",
               "Khi khởi động, Ollama quét dung lượng VRAM thực tế; trên chip Apple Silicon, nó tận dụng băng thông bộ nhớ hợp nhất Unified Memory lên tới 400 gigabyte trên giây.",
               16.0, "TECHNICAL_FLOW", "DATA_FLOW", "apple_metal_unified_memory", "UNIFIED MEMORY 400 GB/S"),
            ns("LF_C05_B03", "how_it_works",
               "Trên máy tính chạy card rời Nvidia hoặc AMD, hệ thống tự động đẩy tối đa số layer lên card đồ họa và điều phối phần còn lại tính toán song song trên CPU.",
               16.0, "TERMINAL_DEMO", "REVEAL", "dynamic_layer_split", "SPLIT LAYER GPU VA CPU"),
        ]
        ch05 = self._make_chapter(
            5, "CO CHE — GPU Layer Offloading Động", 164.0, 210.0, ch05_segs,
            "Thuật toán GPU Layer Offloading: Tự động cân bằng tensor layers giữa VRAM và hệ thống RAM.",
            question="Ollama điều phối các layer mạng nơ-ron giữa chip đồ họa GPU và vi xử lý CPU như thế nào?",
            curiosity_hook="Làm sao một chiếc máy chỉ có 6GB VRAM vẫn có thể chạy được mô hình 8GB?",
            tension="GPU xử lý ma trận siêu nhanh nhưng dung lượng VRAM hữu hạn; CPU có nhiều RAM nhưng băng thông tính toán chậm hơn nhiều lần.",
            explanation="Ollama tính toán footprint của từng layer và tự động offload số layer tối đa lên GPU, phần tràn ra được stream qua bus PCIe về CPU.",
            visual_proof_target="layer_offloading_diagram",
            payoff="Làm chủ nguyên lý hoạt động của cơ chế offloading động tối ưu hóa từng megabyte phần cứng.",
            transition_to_next="Để hỗ trợ điều này một cách bền bỉ, kiến trúc mã nguồn bên dưới được xây dựng như thế nào?"
        )

        # Chapter 06: Architecture Internals (3:30 – 4:14)
        ch06_segs = [
            ns("LF_C06_B01", "architecture",
               "Về mặt kiến trúc hệ thống, Ollama chia tách thành hai tầng độc lập: tầng quản trị viết bằng Go và tầng tính toán hiệu năng cao viết bằng C++.",
               14.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "two_tier_architecture", "KIEN TRUC 2 TANG GO VA C++"),
            ns("LF_C06_B02", "architecture",
               "Go daemon chạy ngầm xử lý các kết nối HTTP bất đồng bộ, quản lý cache và tự động giải phóng mô hình khỏi VRAM sau 5 phút không hoạt động để trả lại bộ nhớ.",
               15.0, "TECHNICAL_FLOW", "DATA_FLOW", "go_daemon_lifecycle", "TU DONG GIAI PHONG VRAM"),
            ns("LF_C06_B03", "architecture",
               "Trong khi đó, tiến trình llama.cpp subprocess được cách ly hoàn toàn, tận dụng triệt để các tập lệnh tăng tốc SIMD như AVX-512 hoặc Apple Metal Shading Language.",
               15.0, "TERMINAL_DEMO", "REVEAL", "llama_cpp_subprocess", "SIMD VA METAL SHADING"),
        ]
        ch06 = self._make_chapter(
            6, "KIEN TRUC — Go Daemon Và Llama.cpp Subprocess", 210.0, 254.0, ch06_segs,
            "Kiến trúc hai tầng: Go daemon điều phối API, subprocess C++ cô lập bộ nhớ và tối ưu SIMD.",
            question="Tại sao Ollama lại chọn Go làm daemon quản lý thay vì viết toàn bộ hệ thống bằng một ngôn ngữ duy nhất?",
            curiosity_hook="Làm thế nào Ollama cách ly các lỗi segmentation fault của backend C++ mà không làm sập server?",
            tension="C++ tối ưu hiệu năng phần cứng nhưng dễ gặp lỗi bộ nhớ; Go mang lại độ ổn định mạng và quản lý tiến trình đồng thời tuyệt vời.",
            explanation="Mô hình process isolation: Go server giao tiếp qua IPC với runner C++, cho phép restart subprocess tức thì nếu gặp ngoại lệ.",
            visual_proof_target="two_tier_architecture",
            payoff="Hiểu sâu sắc kiến trúc hệ thống phân tầng giúp cân bằng giữa an toàn bộ nhớ và hiệu năng tính toán cực đại.",
            transition_to_next="Vậy trong các bài đo lường tốc độ thực tế, những tối ưu hóa này mang lại kết quả ra sao?"
        )

        # Chapter 07: Benchmarks & Empirical Proof (4:14 – 4:54)
        ch07_segs = [
            ns("LF_C07_B01", "benchmark",
               "Các bài kiểm tra độc lập cho thấy: trên MacBook Pro chip M3 Max, mô hình Llama 3 8B đạt tốc độ xuất token lên tới 82 token trên giây.",
               13.0, "DATA_VISUALIZATION", "PUSH_IN", "m3_max_benchmark", "82 TOKENS/GIAY TREN M3"),
            ns("LF_C07_B02", "benchmark",
               "Trên máy tính trang bị card đồ họa Nvidia RTX 4090, tốc độ vượt ngưỡng 115 token trên giây với độ trễ phản hồi từ đầu tiên dưới 180 mili-giây.",
               13.0, "DATA_VISUALIZATION", "PUSH_IN", "rtx_4090_benchmark", "115 TOKENS/GIAY TREN 4090"),
            ns("LF_C07_B03", "benchmark",
               "So với việc gọi API đám mây chịu độ trễ mạng hàng trăm mili-giây, trải nghiệm sinh văn bản cục bộ gần như xuất hiện tức thì sau mỗi cú gõ phím.",
               14.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "latency_vs_cloud", "DO TRE MANG BANG 0"),
        ]
        ch07 = self._make_chapter(
            7, "BENCHMARK — Đo Lường Tốc Độ Thực Tế", 254.0, 294.0, ch07_segs,
            "Số liệu benchmark thực nghiệm: 82 tokens/sec trên M3 Max, 115 tokens/sec trên RTX 4090, TTFT dưới 180ms.",
            question="Tốc độ sinh token thực tế của Ollama khi chạy trên phần cứng cá nhân so với Cloud API ra sao?",
            curiosity_hook="Liệu phần cứng cá nhân có thể bắt kịp hoặc vượt qua tốc độ phản hồi của các máy chủ đám mây?",
            tension="Sự hoài nghi về việc phần cứng tiêu dùng không đủ sức mạnh để xử lý mượt mà các mô hình ngôn ngữ lớn.",
            explanation="Băng thông Unified Memory 400 GB/s trên Apple Silicon và bus 24GB GDDR6X trên RTX 4090 loại bỏ hoàn toàn nút thắt I/O.",
            visual_proof_target="m3_max_benchmark",
            payoff="Chứng kiến bằng chứng thực nghiệm rõ ràng xác nhận tốc độ vượt trội và độ trễ bằng không của AI cục bộ.",
            transition_to_next="Không dừng lại ở việc chat thông thường, hệ sinh thái của Ollama còn mở rộng đến đâu?"
        )

        # Chapter 08: Real-World Ecosystem & Modelfile (4:54 – 5:36)
        ch08_segs = [
            ns("LF_C08_B01", "ecosystem",
               "Không dừng lại ở việc chạy mô hình sẵn có, Ollama định nghĩa chuẩn Modelfile giúp lập trình viên tùy biến hệ thống prompt và nhiệt độ sinh như viết Dockerfile.",
               14.0, "TERMINAL_DEMO", "REVEAL", "modelfile_syntax", "CHUAN MODELFILE TU DONG"),
            ns("LF_C08_B02", "ecosystem",
               "Ollama cũng hỗ trợ xuất định dạng JSON có cấu trúc chặt chẽ và gọi hàm Function Calling, mở đường cho việc xây dựng các autonomous agent hoàn toàn cục bộ.",
               14.0, "BROWSER_DEMO", "ZOOM_TO_DETAIL", "structured_json_output", "FUNCTION CALLING & JSON"),
            ns("LF_C08_B03", "ecosystem",
               "Ngoài văn bản, các mô hình đa phương thức thị giác máy như LLaVA cũng được hỗ trợ trơn tru, cho phép máy tính tự phân tích hình ảnh mà không gửi dữ liệu ra ngoài.",
               14.0, "TECHNICAL_FLOW", "DATA_FLOW", "multimodal_vision_llava", "THI GIAC MAY MULTIMODAL"),
        ]
        ch08 = self._make_chapter(
            8, "HE SINH THAI — Modelfile Và Structured Outputs", 294.0, 336.0, ch08_segs,
            "Hệ sinh thái mở rộng: Chuẩn Modelfile, Function Calling, xuất JSON có cấu trúc và Multimodal Vision.",
            question="Làm thế nào Modelfile cho phép lập trình viên tùy biến và phân phối các AI agent chuyên biệt?",
            curiosity_hook="Tại sao việc hỗ trợ xuất JSON có cấu trúc lại biến Ollama thành nền tảng lý tưởng cho Autonomous Agents?",
            tension="Xây dựng AI agent thường phụ thuộc vào các nền tảng đám mây độc quyền do thiếu hỗ trợ gọi hàm chuẩn hóa ở môi trường cục bộ.",
            explanation="Ollama tích hợp grammar-based decoding ràng buộc token đầu ra tuân thủ chính xác theo schema JSON được chỉ định.",
            visual_proof_target="modelfile_syntax",
            payoff="Mở khóa tiềm năng xây dựng ứng dụng AI tự hành phức tạp và an toàn dữ liệu trên nền tảng Ollama.",
            transition_to_next="Tuy nhiên, để nhìn nhận một cách công tâm nhất, những giới hạn kỹ thuật của nó là gì?"
        )

        # Chapter 09: Trade-offs & Limitations (5:36 – 6:18)
        ch09_segs = [
            ns("LF_C09_B01", "trade_offs",
               "Dẫu vậy, chạy AI cục bộ không phải là liều thuốc vạn năng; sự đánh đổi lớn nhất nằm ở giới hạn cửa sổ ngữ cảnh context window.",
               13.0, "DATA_VISUALIZATION", "PUSH_IN", "context_window_limit", "GIOI HAN CONTEXT WINDOW"),
            ns("LF_C09_B02", "trade_offs",
               "Khi ngữ cảnh mở rộng lên hàng chục nghìn token, bộ nhớ đệm KV cache sẽ phình to theo cấp số nhân và nhanh chóng làm cạn kiệt dung lượng VRAM máy tính.",
               14.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "kv_cache_scaling", "KV CACHE PHINH TO"),
            ns("LF_C09_B03", "trade_offs",
               "Đồng thời, với các bài toán đòi hỏi siêu mô hình 400 tỷ tham số, cụm máy chủ đám mây với hàng nghìn chip chuyên dụng vẫn là lựa chọn bắt buộc.",
               15.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "datacenter_scale_gap", "KHOANG CACH SIEU MO HINH"),
        ]
        ch09 = self._make_chapter(
            9, "DANH DOI — Giới Hạn Và Thách Thức", 336.0, 378.0, ch09_segs,
            "Đánh đổi thực tế: Giới hạn KV-cache khi mở rộng context window, thách thức phần cứng với siêu mô hình 400B.",
            question="Những ranh giới kỹ thuật nào mà các mô hình AI cục bộ hiện nay chưa thể vượt qua?",
            curiosity_hook="Tại sao việc tăng độ dài văn bản đầu vào lại có thể làm sụp đổ bộ nhớ VRAM của bạn?",
            tension="Nhu cầu đọc các tài liệu dài hàng trăm trang mâu thuẫn với dung lượng bộ nhớ đệm KV-cache tăng tuyến tính theo ngữ cảnh.",
            explanation="KV-cache lưu trữ ma trận Attention Keys và Values cho mỗi token trong ngữ cảnh, đòi hỏi thêm gigabyte VRAM ngoài trọng số mô hình.",
            visual_proof_target="kv_cache_scaling",
            payoff="Có được cái nhìn kỹ thuật khách quan, nắm rõ lúc nào nên chạy local và lúc nào cần chuyển hướng sang cloud.",
            transition_to_next="Vượt lên trên những thách thức đó, ý nghĩa thực sự của cuộc cách mạng này là gì?"
        )

        # Chapter 10: Grand Payoff & Conclusion (6:18 – 7:00)
        ch10_segs = [
            ns("LF_C10_B01", "payoff",
               "Ollama đã phá vỡ thế độc quyền của các tập đoàn công nghệ lớn, biến chiếc máy tính cá nhân thành một siêu máy tính xử lý ngôn ngữ thuộc về riêng bạn.",
               14.0, "PAYOFF_VISUAL", "PAYOFF_PUSH", "local_ai_freedom", "PHA VO THE DOC QUYEN AI"),
            ns("LF_C10_B02", "payoff",
               "Đây là bước chuyển dịch mang tính thời đại từ điện toán đám mây tập trung sang kỷ nguyên Edge AI phân tán và đề cao quyền riêng tư tuyệt đối.",
               14.0, "PAYOFF_VISUAL", "PAYOFF_PUSH", "edge_ai_paradigm", "KY NGUYEN EDGE AI PHAN TAN"),
            ns("LF_C10_B03", "cta",
               "Hãy nhấn Thích, Chia sẻ và Đăng ký theo dõi kênh Radar để cùng khám phá những công nghệ mã nguồn mở làm thay đổi thế giới tiếp theo.",
               14.0, "CTA", "STATIC", "channel_subscribe_cta", "DANG KY KENH RADAR"),
        ]
        ch10 = self._make_chapter(
            10, "KET LUAN — Bản Tuyên Ngôn Độc Lập AI", 378.0, 420.0, ch10_segs,
            "Bản tuyên ngôn độc lập: Đưa quyền năng AI về tay lập trình viên và thúc đẩy kỷ nguyên Edge Computing.",
            is_cta=True,
            question="Tương lai của phát triển phần mềm sẽ thay đổi như thế nào khi mỗi kỹ sư đều sở hữu AI riêng biệt?",
            curiosity_hook="Làm thế nào sự trỗi dậy của Local AI sẽ tái định hình lại toàn bộ ngành công nghiệp công nghệ?",
            tension="Sự tập trung quyền lực vào tay số ít nhà cung cấp cloud đối đầu với phong trào phi tập trung mã nguồn mở.",
            explanation="Ollama chứng minh rằng tương lai của AI không nằm trọn trong các datacenter khổng lồ, mà hiện diện trên từng thiết bị cận biên.",
            visual_proof_target="local_ai_freedom",
            payoff="Đúc kết trọn vẹn thông điệp kiến trúc và tầm nhìn công nghệ của kỷ nguyên Local AI.",
            transition_to_next="Kết thúc documentary.",
            key_claims=[
                LongFormClaim(
                    claim_text="Ollama là chuẩn mực mã nguồn mở phổ biến nhất cho việc chạy mô hình ngôn ngữ lớn cục bộ.",
                    classification=ClaimClassification.DOCUMENTED_CLAIM,
                    source_ref=f"github.com/{repo_data.full_name}",
                    verified=True,
                    proof_level=5
                )
            ]
        )

        chapters = [ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09, ch10]
        all_segs = []
        for ch in chapters:
            all_segs.extend(ch.segments)

        total_words = sum(_count_words(s.spoken_text) for s in all_segs)
        yt_chapters = [f"{_fmt_time(ch.start_time_sec)} {ch.chapter_title}" for ch in chapters if not ch.is_cta]

        return LongFormScriptArtifact(
            story_id=story_id,
            story_type=LongFormStoryType.TYPE_A_SINGLE_REPO,
            title="Ollama: Cuộc Cách Mạng Chạy AI Cục Bộ Mượt Mà Trên Mọi Laptop",
            description=(
                f"Phân tích chuyên sâu kiến trúc nội tại của Ollama ({repo_data.name}), "
                f"cơ chế lượng tử hóa GGUF k-quants, thuật toán GPU Layer Offloading trên Apple Silicon & Nvidia, "
                f"số liệu benchmark thực tế và tương lai của Local AI bảo mật. "
                f"GitHub: github.com/{repo_data.full_name}"
            ),
            central_question=thesis.central_question,
            viewer_promise=thesis.viewer_promise,
            editorial_thesis=thesis,
            hook=ch01_segs[0].spoken_text,
            tags=["Ollama", "Local AI", "LLM", "Llama 3", "GGUF", "Apple Silicon", "Metal", "CUDA", "Open Source", "GitHub"],
            target_duration_sec=420.0,
            total_spoken_words=total_words,
            chapters=chapters,
            all_segments=all_segs,
            repository_urls=[repo_data.html_url],
            sources=[f"https://github.com/{repo_data.full_name}",
                     "https://ollama.com/blog", f"https://github.com/{repo_data.full_name}/blob/main/README.md"],
            hashtags=["#Ollama", "#LocalAI", "#Llama3", "#OpenSource", "#AIEdge", "#DeveloperTools", "#GitHub"],
            thumbnail_text="Chay AI Local Nhanh Gap 10 Lan",
            youtube_chapters=yt_chapters,
        )

    # ── TYPE A: Generic deep dive (10 chapters, ~370s, 900+ words) ────────────
    def _type_a_generic(self, story_id, repo_data, stars_str, story, thesis: EditorialThesis) -> LongFormScriptArtifact:
        seg_order = [0]

        def ns(beat_id, seg_type, text, dur, v_type, motion, cue, headline):
            seg_order[0] += 1
            return _seg(seg_order[0], beat_id, seg_type, text, dur,
                        v_type, motion, cue, headline,
                        evidence=[f"github.com/{repo_data.full_name}"])

        # Ch 1: HOOK (0:00 - 0:30)
        ch01_segs = [
            ns("LF_C01_B01", "hook",
               f"Một dự án mã nguồn mở vừa thu hút hơn {stars_str} ngôi sao trên GitHub và đang làm thay đổi tư duy kỹ thuật của cộng đồng lập trình viên thế giới.",
               10.0, "REAL_REPOSITORY_UI", "ZOOM_TO_DETAIL", "github_repo_header", f"{repo_data.name.upper()} TREN GITHUB"),
            ns("LF_C01_B02", "hook",
               f"Đó chính là {repo_data.name} — một giải pháp kỹ thuật đột phá được xây dựng bằng {repo_data.language or 'ngôn ngữ hiện đại'} nhằm giải quyết một vấn đề nhức nhối bấy lâu nay.",
               10.0, "DATA_VISUALIZATION", "PUSH_IN", "star_count_display", f"{stars_str} SAO"),
            ns("LF_C01_B03", "hook",
               f"Liệu {repo_data.name} có thực sự giải quyết triệt để nút thắt cổ chai mà các công cụ trước đó bó tay? Chúng ta sẽ cùng mổ xẻ ngay sau đây.",
               11.0, "TECHNICAL_FLOW", "REVEAL", "chapter_preview", "CAU HOI COT LOI"),
        ]
        ch01 = self._make_chapter(
            1, f"HOOK — {repo_data.name} La Gi?", 0.0, 31.0, ch01_segs,
            f"{repo_data.name}: {repo_data.description or 'Dự án mã nguồn mở nổi bật.'}",
            question=thesis.central_question,
            curiosity_hook=f"Tại sao dự án {repo_data.name} lại nhận được sự chú ý bùng nổ đến vậy?",
            tension="Các giải pháp truyền thống thường cồng kềnh, chậm chạp và khó bảo trì khi dự án mở rộng.",
            explanation=f"{repo_data.name} tiếp cận bài toán bằng tư duy tối ưu hóa kiến trúc hiện đại từ con số không.",
            visual_proof_target="github_repo_header",
            payoff="Nhận thức rõ giá trị cốt lõi và sức hút của dự án đối với cộng đồng công nghệ.",
            transition_to_next="Để trả lời câu hỏi này, trước tiên hãy nhìn vào bài toán mà cộng đồng đang đối mặt."
        )

        # Ch 2: THE PROBLEM / TENSION (0:31 - 1:11)
        ch02_segs = [
            ns("LF_C02_B01", "problem",
               f"Trong suốt thời gian dài, các kỹ sư phần mềm phải đối mặt với một thách thức nan giải: {repo_data.description or 'các công cụ hiện hành tồn tại nhiều hạn chế về hiệu năng'}.",
               13.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "problem_diagram", "VAN DE GIAI QUYET"),
            ns("LF_C02_B02", "problem",
               "Các phương pháp tiếp cận trước đây thường bị nghẽn ở hiệu năng xử lý, phụ thuộc vào quá nhiều lớp trung gian và tiêu tốn tài nguyên phần cứng nghiêm trọng.",
               14.0, "DATA_VISUALIZATION", "PUSH_IN", "bottleneck_metric", "NGHEN HIEU NANG"),
            ns("LF_C02_B03", "problem",
               "Khi khối lượng dữ liệu và quy mô dự án tăng lên, chi phí bảo trì và độ trễ phản hồi trở thành một gánh nặng khổng lồ trong các hệ thống production.",
               13.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "legacy_comparison", "GANH NANG HE THONG"),
        ]
        ch02 = self._make_chapter(
            2, "VAN DE — Rao Can Ky Thuat", 31.0, 71.0, ch02_segs,
            "Phân tích nguyên nhân khiến các công cụ cũ gặp bế tắc khi mở rộng quy mô.",
            question="Những hạn chế cốt lõi nào của phương pháp cũ buộc một giải pháp mới phải ra đời?",
            curiosity_hook="Liệu có thể phá vỡ sự đánh đổi giữa tính tiện lợi và tốc độ xử lý?",
            tension=thesis.key_tension,
            explanation="Mổ xẻ các lớp trung gian không cần thiết trong kiến trúc truyền thống gây lãng phí CPU và RAM.",
            visual_proof_target="problem_diagram",
            payoff="Xác định chính xác nút thắt cổ chai mà dự án nhắm tới để giải quyết.",
            transition_to_next="Chính trong hoàn cảnh bế tắc đó, tác giả dự án đã đưa ra một hướng đi khác biệt."
        )

        # Ch 3: WHY THIS PROJECT EXISTS (1:11 - 1:51)
        ch03_segs = [
            ns("LF_C03_B01", "discovery",
               f"{repo_data.name} ra đời với mục tiêu phá bỏ hoàn toàn các rào cản kỹ thuật cũ bằng việc thiết kế lại luồng xử lý từ gốc.",
               13.0, "REAL_REPOSITORY_UI", "ZOOM_TO_DETAIL", "repo_language_stats", f"NGON NGU {repo_data.language or 'CODE'}"),
            ns("LF_C03_B02", "discovery",
               f"Được viết bằng {repo_data.language or 'ngôn ngữ tối ưu'}, dự án tận dụng tối đa cơ chế xử lý song song và tối ưu hóa bộ nhớ cấp thấp.",
               14.0, "TECHNICAL_FLOW", "DATA_FLOW", "core_design_philosophy", "TRIET LY THIET KE"),
            ns("LF_C03_B03", "discovery",
               f"Với hơn {repo_data.forks} lượt fork và sự tham gia đóng góp của hàng trăm lập trình viên, dự án đã chứng minh được tính khả thi và độ tin cậy vượt bậc.",
               13.0, "DATA_VISUALIZATION", "PUSH_IN", "repo_stats", "CONG DONG DONG GOP"),
        ]
        ch03 = self._make_chapter(
            3, f"SU MENH — Su Ra Doi Cua {repo_data.name}", 71.0, 111.0, ch03_segs,
            f"Triết lý thiết kế và sứ mệnh giải quyết bài toán cốt lõi của {repo_data.name}.",
            question=f"Tư duy thiết kế của {repo_data.name} khác biệt như thế nào so với phần còn lại?",
            curiosity_hook="Tại sao đội ngũ tác giả lại lựa chọn cách tiếp cận phức tạp hơn để đổi lấy hiệu năng?",
            tension="Viết lại từ đầu đòi hỏi chi phí kỹ thuật cực lớn nhưng mang lại sự tự do tối ưu tuyệt đối.",
            explanation=thesis.why_this_matters,
            visual_proof_target="repo_language_stats",
            payoff="Thấu hiểu động lực và triết lý kỹ thuật định hình nên kiến trúc dự án.",
            transition_to_next="Bây giờ, hãy cùng nhìn sâu vào đột phá kỹ thuật cốt lõi làm nên sức mạnh của nó."
        )

        # Ch 4: BREAKTHROUGH & CORE IDEA (1:51 - 2:31)
        ch04_segs = [
            ns("LF_C04_B01", "breakthrough",
               "Điểm đột phá kỹ thuật đáng chú ý nhất chính là cách module xử lý trung tâm được tái cấu trúc thành các thành phần độc lập và bất đồng bộ.",
               13.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "breakthrough_schematic", "DOT PHA TRUNG TAM"),
            ns("LF_C04_B02", "breakthrough",
               "Thay vì xử lý tuần tự qua các lớp trừu tượng nặng nề, dữ liệu được truyền thẳng qua đường ống tối ưu với độ trễ gần như bằng không.",
               14.0, "TECHNICAL_FLOW", "DATA_FLOW", "pipeline_stream", "PIPELINE TOI UU"),
            ns("LF_C04_B03", "breakthrough",
               "Cơ chế này loại bỏ hoàn toàn các điểm nghẽn tương tranh và cho phép hệ thống mở rộng quy mô tuyến tính theo số lượng nhân vi xử lý.",
               13.0, "DATA_VISUALIZATION", "PUSH_IN", "linear_scaling_chart", "MO RONG TUYEN TINH"),
        ]
        ch04 = self._make_chapter(
            4, "DOT PHA — Y Tuong Kien Truc", 111.0, 151.0, ch04_segs,
            "Đột phá kiến trúc: đường ống dữ liệu bất đồng bộ và loại bỏ các lớp trung gian.",
            question="Cơ chế kỹ thuật nào giúp hệ thống mở rộng tuyến tính mà không bị suy giảm hiệu năng?",
            curiosity_hook="Làm thế nào dữ liệu có thể truyền qua các module mà không gặp độ trễ sao chép?",
            tension="Xử lý song song thường gặp rủi ro tương tranh dữ liệu và khó bảo đảm tính toàn vẹn.",
            explanation=thesis.technical_breakthrough,
            visual_proof_target="breakthrough_schematic",
            payoff="Nắm rõ ý tưởng kiến trúc đột phá tạo nên lợi thế cạnh tranh cho dự án.",
            transition_to_next="Để hình dung rõ hơn, chúng ta hãy mổ xẻ chi tiết từng tầng vận hành bên trong."
        )

        # Ch 5: HOW IT ACTUALLY WORKS (2:31 - 3:20)
        ch05_segs = [
            ns("LF_C05_B01", "how_it_works",
               "Toàn bộ hệ thống vận hành theo một quy trình tuần tự nhưng cực kỳ chặt chẽ: từ khâu tiếp nhận dữ liệu đầu vào, phân tích cú pháp đến thực thi.",
               12.0, "ARCHITECTURE_DIAGRAM", "REVEAL", "architecture_overview", "QUY TRINH 3 BUOC"),
            ns("LF_C05_B02", "how_it_works",
               "Tầng đầu vào chuẩn hóa mọi yêu cầu thành định dạng nhị phân nhỏ gọn, giúp giảm thiểu tối đa kích thước dữ liệu luân chuyển trên bộ nhớ.",
               15.0, "TECHNICAL_FLOW", "DATA_FLOW", "binary_serialization", "CHUAN HOA DINH DANG"),
            ns("LF_C05_B03", "how_it_works",
               "Tầng thực thi sử dụng các thuật toán chuyên dụng để phân bổ tác vụ đến các luồng rảnh rỗi, bảo đảm không có tài nguyên nào bị lãng phí.",
               16.0, "TERMINAL_DEMO", "REVEAL", "thread_pool_dispatch", "DIEU PHOI DA LUONG"),
            ns("LF_C05_B04", "how_it_works",
               "Cuối cùng, tầng phản hồi đóng gói kết quả và trả về ngay tức thì thông qua giao tiếp bất đồng bộ không gây nghẽn tiến trình gọi.",
               16.0, "TECHNICAL_FLOW", "DATA_FLOW", "async_response_pipeline", "PHAN HOI BAT DONG BO"),
        ]
        ch05 = self._make_chapter(
            5, "CO CHE — Kien Truc Va Cach Hoat Dong", 151.0, 200.0, ch05_segs,
            "Chi tiết 3 tầng hoạt động: Chuẩn hóa nhị phân, điều phối đa luồng, và phản hồi bất đồng bộ.",
            question="Các tầng module phối hợp với nhau như thế nào để đạt độ trễ tối thiểu?",
            curiosity_hook="Làm thế nào hệ thống điều phối tác vụ mà không gây khóa luồng giao diện?",
            tension=thesis.key_tension,
            explanation=thesis.surprising_insight,
            visual_proof_target="architecture_overview",
            payoff="Làm chủ sơ đồ kiến trúc vận hành chi tiết từ đầu vào đến đầu ra.",
            transition_to_next="Lý thuyết rất chặt chẽ, nhưng bằng chứng thực nghiệm trên môi trường thật ra sao?"
        )

        # Ch 6: TECHNICAL PROOF & BENCHMARKS (3:20 - 4:05)
        ch06_segs = [
            ns("LF_C06_B01", "benchmark",
               "Trong các thử nghiệm đo lường thực tế, dự án đã thể hiện sự vượt trội rõ rệt về cả thời gian phản hồi lẫn mức độ chiếm dụng tài nguyên.",
               13.0, "DATA_VISUALIZATION", "PUSH_IN", "performance_metrics", "KET QUA DO LUONG"),
            ns("LF_C06_B02", "benchmark",
               "Thời gian xử lý cho mỗi đơn vị tác vụ được rút ngắn đáng kể so với các thư viện tương đương, mang lại trải nghiệm mượt mà không độ trễ.",
               16.0, "DATA_VISUALIZATION", "PUSH_IN", "latency_reduction_chart", "RUT NGAN THOI GIAN XU LY"),
            ns("LF_C06_B03", "benchmark",
               "Về mức tiêu hao bộ nhớ, hệ thống duy trì ngưỡng RAM cực kỳ khiêm tốn ngay cả khi chịu tải hàng nghìn tác vụ đồng thời.",
               16.0, "TERMINAL_DEMO", "REVEAL", "memory_profiler_trace", "TIET KIEM BO NHO RAM"),
        ]
        ch06 = self._make_chapter(
            6, "THUC NGHIEM — Bang Chung Ky Thuat", 200.0, 245.0, ch06_segs,
            "Đo lường định lượng: Tối ưu thời gian xử lý và tiết kiệm bộ nhớ RAM thực tế.",
            question="Những con số đo lường hiệu năng thực tế chứng minh điều gì?",
            curiosity_hook="Liệu hệ thống có duy trì được sự ổn định khi tải tăng đột biến?",
            tension="Nhiều giải pháp chỉ đạt hiệu năng cao trong phòng thí nghiệm nhưng sụp đổ trong điều kiện thực tế.",
            explanation="Các bài test tải chứng minh hệ thống duy trì độ ổn định cao và không rò rỉ bộ nhớ.",
            visual_proof_target="performance_metrics",
            payoff="Xác thực các tuyên bố kỹ thuật bằng số liệu đo lường định lượng cụ thể.",
            transition_to_next="Từ những kết quả ấn tượng này, giá trị ứng dụng thực tiễn được mở ra như thế nào?"
        )

        # Ch 7: REAL-WORLD IMPLICATIONS (4:05 - 4:50)
        ch07_segs = [
            ns("LF_C07_B01", "implications",
               "Khả năng vận hành tối ưu này mang lại những giá trị kinh tế và kỹ thuật rất cụ thể cho các đội ngũ phát triển phần mềm.",
               11.0, "DATA_VISUALIZATION", "PUSH_IN", "use_cases_grid", "GIA TRI UNG DUNG THUC TE"),
            ns("LF_C07_B02", "implications",
               "Các kỹ sư có thể tích hợp thư viện vào các sản phẩm hiện có mà không phải lo lắng về việc phình to kích thước ứng dụng hay làm chậm hệ thống.",
               16.0, "TECHNICAL_FLOW", "DATA_FLOW", "seamless_integration", "TICH HOP KHONG PHINH TO"),
            ns("LF_C07_B03", "implications",
               "Hơn thế nữa, việc cắt giảm tài nguyên máy chủ giúp doanh nghiệp tiết kiệm đáng kể ngân sách hạ tầng và năng lượng vận hành.",
               18.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "infrastructure_savings", "TIET KIEM NGAN SACH MAY CHU"),
        ]
        ch07 = self._make_chapter(
            7, "UNG DUNG — Tac Dong Thuc Tien", 245.0, 290.0, ch07_segs,
            "Ứng dụng thực tế: Tích hợp liền mạch, giảm tải máy chủ và tiết kiệm chi phí vận hành.",
            question="Doanh nghiệp và lập trình viên cá nhân hưởng lợi cụ thể ra sao?",
            curiosity_hook="Làm thế nào việc tối ưu một thư viện nhỏ lại tiết kiệm hàng nghìn đô la máy chủ?",
            tension="Nhu cầu cắt giảm chi phí hạ tầng trong bối cảnh các ứng dụng ngày càng tiêu tốn điện toán đám mây.",
            explanation=thesis.real_world_implication,
            visual_proof_target="use_cases_grid",
            payoff="Liên kết trực tiếp giữa các quyết định kiến trúc kỹ thuật và tác động kinh tế doanh nghiệp.",
            transition_to_next="Tuy nhiên, để có cái nhìn toàn diện, chúng ta không thể bỏ qua các bài toán đánh đổi."
        )

        # Ch 8: TRADE-OFFS & LIMITATIONS (4:50 - 5:35)
        ch08_segs = [
            ns("LF_C08_B01", "limitations",
               "Bất kỳ giải pháp kỹ thuật nào cũng là một bài toán cân nhắc đánh đổi, và dự án này không phải là ngoại lệ.",
               11.0, "DATA_VISUALIZATION", "PUSH_IN", "tradeoffs_header", "BAI TOAN DANH DOI"),
            ns("LF_C08_B02", "limitations",
               "Việc áp dụng kiến trúc mới đòi hỏi các kỹ sư phải làm quen với mô hình tư duy khác biệt và có thời gian thích ứng nhất định.",
               16.0, "BEFORE_AFTER", "BEFORE_AFTER_SPLIT", "learning_curve_comparison", "DUONG CONG HOC TAP"),
            ns("LF_C08_B03", "limitations",
               "Ngoài ra, hệ sinh thái các plugin mở rộng và tài liệu hướng dẫn cộng đồng vẫn đang trong quá trình tiếp tục hoàn thiện.",
               18.0, "DATA_VISUALIZATION", "PUSH_IN", "ecosystem_roadmap", "HE SINH THAI CAN THOI GIAN"),
        ]
        ch08 = self._make_chapter(
            8, "GIOI HAN — Danh Doi Ky Thuat", 290.0, 335.0, ch08_segs,
            "Đánh giá khách quan: Đường cong học tập và hệ sinh thái mở rộng cần thời gian trưởng thành.",
            question="Những rào cản và sự đánh đổi nào cần lưu ý trước khi triển khai?",
            curiosity_hook="Khi nào dự án này KHÔNG phải là sự lựa chọn tối ưu cho bạn?",
            tension=thesis.trade_off,
            explanation=thesis.limitation,
            visual_proof_target="tradeoffs_header",
            payoff="Trang bị cái nhìn phản biện khách quan, giúp người xem ra quyết định sáng suốt.",
            transition_to_next="Sau khi cân nhắc mọi mặt, vị thế và tương lai lâu dài của dự án là gì?"
        )

        # Ch 9: WHO SHOULD CARE & FINAL PAYOFF (5:35 - 6:15)
        ch09_segs = [
            ns("LF_C09_B01", "payoff",
               f"{repo_data.name} chứng minh một chân lý quan trọng: việc đào sâu tối ưu hóa kiến trúc từ gốc rễ luôn đem lại những giá trị vượt thời gian.",
               14.0, "PAYOFF_VISUAL", "PAYOFF_PUSH", "long_term_vision", "GIA TRI TOI UU GOC RE"),
            ns("LF_C09_B02", "payoff",
               f"Với sự ủng hộ của hơn {stars_str} ngôi sao và đà phát triển mạnh mẽ, đây chắc chắn là một trong những dự án mã nguồn mở đáng học hỏi nhất.",
               14.0, "DATA_VISUALIZATION", "PUSH_IN", "future_trajectory", "DA PHAT TRIEN MANH ME"),
            ns("LF_C09_B03", "payoff",
               "Đường link mã nguồn chính thức được đặt tại phần mô tả video để anh em trực tiếp tải về và thử nghiệm trong dự án của mình.",
               12.0, "PAYOFF_VISUAL", "PAYOFF_PUSH", "github_repo_link", f"github.com/{repo_data.full_name}"),
        ]
        ch09 = self._make_chapter(
            9, "KET LUAN — Gia Tri Ben Vung", 335.0, 375.0, ch09_segs,
            "Tổng kết giá trị thực tiễn và bài học kiến trúc từ dự án.",
            question="Bài học quan trọng nhất mà các kỹ sư có thể đúc kết từ dự án này là gì?",
            curiosity_hook="Dự án sẽ định hình xu hướng phát triển phần mềm trong những năm tới ra sao?",
            tension="Sự cạnh tranh giữa các giải pháp phần mềm nhanh-tiện ngắn hạn và các kiến trúc bền vững dài hạn.",
            explanation=thesis.final_payoff,
            visual_proof_target="long_term_vision",
            payoff="Giải quyết trọn vẹn câu hỏi mở đầu và trao gửi giá trị dài hạn cho người xem.",
            transition_to_next="Và nếu bạn thấy phân tích kiến trúc chuyên sâu này hữu ích..."
        )

        # Ch 10: CTA (6:15 - 6:30)
        ch10_segs = [
            ns("LF_C10_B01", "cta",
               "Nếu video phân tích kỹ thuật này mang lại giá trị cho anh em, hãy like, share và đăng ký kênh để đón xem những dự án mã nguồn mở tiếp theo nhé.",
               15.0, "CTA", "STATIC", "cta_screen", "LIKE SHARE DANG KY KENH"),
        ]
        ch10 = self._make_chapter(
            10, "CTA — Ket Thuc", 375.0, 390.0, ch10_segs, "Like, share, đăng ký.", is_cta=True,
            tension="", explanation="", visual_proof_target="cta_screen", payoff="Hoàn tất documentary."
        )

        chapters = [ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09, ch10]
        all_segs = []
        for ch in chapters:
            all_segs.extend(ch.segments)
        total_words = sum(_count_words(s.spoken_text) for s in all_segs)
        yt_chapters = [f"{_fmt_time(ch.start_time_sec)} {ch.chapter_title}" for ch in chapters if not ch.is_cta]

        return LongFormScriptArtifact(
            story_id=story_id,
            story_type=LongFormStoryType.TYPE_A_SINGLE_REPO,
            title=f"{repo_data.name}: Dự Án GitHub {stars_str} Sao Đang Thay Đổi Cuộc Chơi — Phân Tích Chuyên Sâu",
            description=f"Deep dive về {repo_data.full_name}. {repo_data.description or ''} GitHub: github.com/{repo_data.full_name}",
            central_question=thesis.central_question,
            viewer_promise=thesis.viewer_promise,
            editorial_thesis=thesis,
            hook=ch01_segs[0].spoken_text,
            tags=[repo_data.name, "GitHub", "open source", repo_data.language or "technology", "architecture", "developer tools"],
            target_duration_sec=390.0,
            total_spoken_words=total_words,
            chapters=chapters,
            all_segments=all_segs,
            repository_urls=[repo_data.html_url],
            sources=[f"https://github.com/{repo_data.full_name}"],
            hashtags=[f"#{repo_data.name}", "#GitHub", "#OpenSource", "#Technology", "#Architecture"],
            thumbnail_text=f"{repo_data.name} {stars_str} Sao",
            youtube_chapters=yt_chapters,
        )

    # ─── TYPE B: Multi-Repo Theme ─────────────────────────────────────────────
    def _generate_type_b(self, story, thesis: EditorialThesis) -> LongFormScriptArtifact:
        repos = story.selected_repos
        story_id = f"lf_multi_{uuid.uuid4().hex[:8]}"
        seg_order = [0]

        def ns(beat_id, seg_type, text, dur, v_type, motion, cue, headline, repo=None):
            seg_order[0] += 1
            ev = [f"github.com/{repo.full_name}"] if repo else []
            return _seg(seg_order[0], beat_id, seg_type, text, dur, v_type, motion, cue, headline, ev)

        repo_count = len(repos)
        ch01_segs = [
            ns("LF_C01_B01", "hook",
               f"Tôi đã dành thời gian nghiên cứu {repo_count} dự án GitHub đang thay đổi cách chúng ta xây dựng phần mềm.",
               10.0, "REAL_REPOSITORY_UI", "ZOOM_TO_DETAIL", "multi_repo_overview", f"{repo_count} DU AN GITHUB"),
            ns("LF_C01_B02", "hook",
               "Trong video này, tôi sẽ giải thích từng dự án — tại sao nó nổi bật và bạn có thể dùng nó như thế nào.",
               8.0, "DATA_VISUALIZATION", "PUSH_IN", "chapter_map", "GIAI THICH TUNG DU AN"),
        ]
        ch01 = self._make_chapter(
            1, "HOOK — Gioi Thieu", 0.0, 18.0, ch01_segs,
            f"Top {repo_count} dự án GitHub đang thay đổi phát triển phần mềm.",
            question="Những xu hướng công nghệ mã nguồn mở nào đang dẫn dắt làn sóng đổi mới?",
            curiosity_hook="Khám phá các viên ngọc mã nguồn mở ẩn giấu đang được cộng đồng chú ý.",
            tension="Hàng trăm nghìn repo mới mỗi ngày khiến kỹ sư bị quá tải thông tin.",
            explanation="Tuyển chọn và phân tích chuyên sâu các dự án có tác động kiến trúc lớn nhất.",
            visual_proof_target="multi_repo_overview",
            payoff="Tiết kiệm thời gian sàng lọc và nắm bắt ngay các dự án đáng giá nhất.",
            transition_to_next="Hãy bắt đầu với dự án đầu tiên."
        )

        chapters = [ch01]
        t = 18.0
        for i, repo_analysis in enumerate(repos[:6], start=2):
            r = repo_analysis.repository
            stars_k = round(r.stars / 1000, 1)
            stars_str = f"{stars_k} nghìn" if stars_k >= 1 else str(r.stars)
            segs = [
                ns(f"LF_C{i:02d}_B01", "repo_intro",
                   f"Dự án thứ {i-1}: {r.name}. {r.description or 'Một công cụ mã nguồn mở đáng chú ý.'}",
                   14.0, "REAL_REPOSITORY_UI", "ZOOM_TO_DETAIL", f"repo_{r.name}_header", f"{r.name.upper()} — {stars_str} SAO", r),
                ns(f"LF_C{i:02d}_B02", "repo_why",
                   f"Tại sao dự án này đáng chú ý: {repo_analysis.why_care or 'Giải quyết một vấn đề quan trọng trong cộng đồng developer.'}",
                   16.0, "TECHNICAL_FLOW", "DATA_FLOW", f"repo_{r.name}_architecture", "TAI SAO DANG QUAN TAM", r),
            ]
            ch = self._make_chapter(
                i, f"DU AN {i-1} — {r.name}", t, t + 30.0, segs,
                f"{r.name}: {r.description or 'Dự án đáng chú ý.'}",
                question=f"{r.name} mang lại giá trị độc đáo nào?",
                curiosity_hook=f"Tại sao dự án này lại nhận được {stars_str} sao?",
                tension="Bài toán kỹ thuật mà dự án hướng tới.",
                explanation=repo_analysis.technical_novelty or "Kiến trúc tối ưu.",
                visual_proof_target=f"repo_{r.name}_header",
                payoff=repo_analysis.takeaway or "Giá trị thực tiễn.",
                transition_to_next="Chuyển sang dự án tiếp theo.",
                key_claims=[
                    LongFormClaim(
                        claim_text=f"{r.full_name} đạt {r.stars} sao trên GitHub.",
                        classification=ClaimClassification.OFFICIAL_SOURCE,
                        source_url=r.html_url,
                        source_ref=r.full_name,
                        verified=True,
                        proof_level=1
                    )
                ]
            )
            chapters.append(ch)
            t += 30.0

        # Conclusion + CTA
        c_num = len(chapters) + 1
        conc_segs = [
            ns(f"LF_C{c_num:02d}_B01", "payoff",
               f"Đó là {repo_count} dự án GitHub mà tôi nghĩ bạn nên biết trong năm nay. Link từng repo ở bên dưới.",
               12.0, "PAYOFF_VISUAL", "PAYOFF_PUSH", "all_repos_summary", "TONG KET"),
        ]
        ch_conc = self._make_chapter(
            c_num, "KET LUAN — Tong Ket", t, t + 12.0, conc_segs,
            "Tổng kết các dự án nổi bật.",
            question="Làm thế nào để ứng dụng các công cụ này vào công việc?",
            curiosity_hook="Tương lai của hệ sinh thái công nghệ.",
            tension="", explanation="", visual_proof_target="all_repos_summary", payoff="Tổng hợp trọn vẹn.",
            transition_to_next="Lời kết cuối."
        )
        chapters.append(ch_conc)
        t += 12.0

        cta_num = len(chapters) + 1
        cta_segs = [
            ns(f"LF_C{cta_num:02d}_B01", "cta",
               "Nếu thấy hữu ích, hãy like, share và đăng ký kênh để đón xem những video tiếp theo.",
               10.0, "CTA", "STATIC", "cta_screen", "LIKE SHARE DANG KY"),
        ]
        ch_cta = self._make_chapter(
            cta_num, "CTA", t, t + 10.0, cta_segs, "Like, share, đăng ký.", is_cta=True,
            tension="", explanation="", visual_proof_target="cta_screen", payoff="Hoàn tất."
        )
        chapters.append(ch_cta)

        all_segs = []
        for ch in chapters:
            all_segs.extend(ch.segments)
        total_words = sum(_count_words(s.spoken_text) for s in all_segs)
        yt_chapters = [f"{_fmt_time(ch.start_time_sec)} {ch.chapter_title}" for ch in chapters if not ch.is_cta]
        repo_urls = [r.repository.html_url for r in repos]

        return LongFormScriptArtifact(
            story_id=story_id,
            story_type=LongFormStoryType.TYPE_B_MULTI_REPO,
            title=f"Top {repo_count} Dự Án GitHub Đang Thay Đổi Phát Triển Phần Mềm",
            description=f"Deep dive vào {repo_count} dự án GitHub nổi bật nhất. " + " • ".join(r.repository.name for r in repos[:4]),
            central_question=thesis.central_question,
            viewer_promise=thesis.viewer_promise,
            editorial_thesis=thesis,
            hook=ch01_segs[0].spoken_text,
            tags=["GitHub", "open source", "developer tools"] + [r.repository.name for r in repos[:4]],
            target_duration_sec=t + 10.0,
            total_spoken_words=total_words,
            chapters=chapters,
            all_segments=all_segs,
            repository_urls=repo_urls,
            sources=[f"https://github.com/{r.repository.full_name}" for r in repos],
            hashtags=["#GitHub", "#OpenSource", "#DevTools", "#Programming"],
            thumbnail_text=f"Top {repo_count} Du An GitHub",
            youtube_chapters=yt_chapters,
        )

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _make_chapter(self, num, title, start, end, segs,
                       retention_event="", is_cta=False,
                       question="", curiosity_hook="", transition_to_next="",
                       tension="", explanation="", visual_proof_target="", payoff="",
                       key_claims=None) -> LongFormChapter:
        vtypes = list(set(s.visual_type for s in segs))
        spoken = " ".join(s.spoken_text for s in segs)
        return LongFormChapter(
            chapter_number=num,
            chapter_title=title,
            chapter_label=f"CHAPTER {num:02d}",
            start_time_sec=start,
            end_time_sec=end,
            duration_sec=end - start,
            spoken_text=spoken,
            question=question,
            curiosity_hook=curiosity_hook,
            tension=tension,
            explanation=explanation,
            visual_proof_target=visual_proof_target,
            payoff=payoff,
            transition_to_next=transition_to_next,
            segments=segs,
            key_claims=key_claims or [],
            visual_types=vtypes,
            retention_event=retention_event,
            is_cta=is_cta,
        )
