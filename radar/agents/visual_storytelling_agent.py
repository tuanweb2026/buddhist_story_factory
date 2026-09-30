import os
import re
from typing import Dict, Any, List
from radar.models.schemas import ScriptArtifact, VisualStoryboard, VisualBeatEvent


class VisualStorytellingAgent:
    """Visual Storytelling Engine V3: Narration-Synchronized Visual Storytelling.
    
    Principles:
    1. VOICE FIRST: Visuals prove or illustrate the exact narration claims.
    2. ATTENTION TARGET: Every visual beat declares an attention target.
    3. CAMERA MOVEMENT: Guides the viewer's eyes to the attention target.
    4. NO ORPHAN VISUALS: Every visual is semantically linked to the voice track.
    5. VISUAL PAYOFF: Each beat resolves into a clear takeaway before transition.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.shorts_cfg = config.get("formats", {}).get("shorts", {})
        self.width = self.shorts_cfg.get("width", 1080)
        self.height = self.shorts_cfg.get("height", 1920)

    def plan_storyboard(self, script: ScriptArtifact, repo_category: str = "DEV_TOOL") -> VisualStoryboard:
        beats: List[VisualBeatEvent] = []
        current_time = 0.0

        # Detect repository identity from script title or segments
        is_browser_use = any("browser-use" in (script.title + s.spoken_text).lower() for s in script.segments) or "browser" in repo_category.lower()
        is_omi = any("omi" in (script.title + s.spoken_text).lower() for s in script.segments) or "omi" in repo_category.lower() or "wearable" in repo_category.lower()
        is_zed = any("zed" in (script.title + s.spoken_text).lower() for s in script.segments) or "zed" in repo_category.lower()
        is_ollama = any("ollama" in (script.title + s.spoken_text).lower() for s in script.segments) or "ollama" in repo_category.lower()

        for seg in script.segments:
            dur = seg.estimated_duration_sec
            beat_info = self._map_segment_to_v3_beat(seg, is_browser_use=is_browser_use, is_omi=is_omi, is_zed=is_zed, is_ollama=is_ollama)

            beat = VisualBeatEvent(
                beat_id=seg.beat_id,
                order=seg.order,
                start_time=round(current_time, 2),
                end_time=round(current_time + dur, 2),
                duration_sec=dur,
                narration=seg.spoken_text,
                visual_type=beat_info["visual_type"],
                headline_text=seg.headline_text,
                sub_label=beat_info["sub_label"],
                diagram_elements=beat_info["diagram_elements"],
                motion_type=beat_info["motion_type"],
                semantic_intent=beat_info["semantic_intent"],
                visual_claim=beat_info["visual_claim"],
                attention_target=beat_info["attention_target"],
                visual_action=beat_info["visual_action"],
                payoff=beat_info["payoff"],
                transition=beat_info["transition"],
                evidence_required=True,
                is_synthetic=True,
                synthetic_notice="MINH HỌA KHÁI NIỆM • GITHUB PROJECT RADAR",
                source_attribution=beat_info.get("source_attribution", "Official GitHub Repository Metadata")
            )
            beats.append(beat)
            current_time += dur

        return VisualStoryboard(
            story_id=script.story_id,
            beats=beats,
            total_duration_sec=round(current_time, 2),
            repo_category=repo_category
        )

    def _map_segment_to_v3_beat(self, seg, is_browser_use: bool = False, is_omi: bool = False, is_zed: bool = False, is_ollama: bool = False) -> Dict[str, Any]:
        """Maps narration semantic intent to exact Visual Event Types (A-I), attention targets, camera motions, and payoffs."""
        seg_type = seg.segment_type.lower()
        spoken = seg.spoken_text.lower()

        # Handle CTA strictly first
        if seg_type == "cta" or "like" in spoken or "đăng ký" in spoken:
            return {
                "visual_type": "CTA",
                "sub_label": "THEO DÕI GITHUB RADAR",
                "diagram_elements": ["LIKE", "SHARE", "ĐĂNG KÝ KÊNH"],
                "motion_type": "PUSH_IN",
                "semantic_intent": "Call to action for viewers to like, share and subscribe",
                "visual_claim": "Hành động theo dõi kênh GitHub Project Radar",
                "attention_target": "Nút Like, Share và Đăng ký kênh",
                "visual_action": "Hiển thị nút tương tác nổi bật chuẩn chính sách",
                "payoff": "Đăng ký kênh để đón nhận dự án mới",
                "transition": "Fade to end"
            }

        if is_ollama:
            return self._map_ollama_beat(seg, seg_type, spoken)
        elif is_zed:
            return self._map_zed_beat(seg, seg_type, spoken)
        elif is_browser_use:
            return self._map_browser_use_beat(seg, seg_type, spoken)
        elif is_omi:
            return self._map_omi_beat(seg, seg_type, spoken)
        else:
            return self._map_general_devtool_beat(seg, seg_type, spoken)

    def _map_ollama_beat(self, seg, seg_type: str, spoken: str) -> Dict[str, Any]:
        """Semantic beat mapping for Ollama (Local AI runner, GGUF quants, GPU layer offload, zero cost privacy)."""
        if seg_type == "hook":
            return {
                "visual_type": "REAL_REPOSITORY_UI",
                "sub_label": "TRENDING REPOSITORY // LOCAL AI RUNTIME",
                "diagram_elements": ["ollama/ollama", "181K+ STARS", "GO + C++", "OPEN SOURCE"],
                "motion_type": "ZOOM_TO_DETAIL",
                "semantic_intent": "Establish Ollama as the global standard for running LLMs locally with zero API cost",
                "visual_claim": "Ollama chạy Llama 3 và DeepSeek mượt mà ngay trên máy cá nhân",
                "attention_target": "Huy hiệu 181K+ Stars và thông số cấu hình cục bộ",
                "visual_action": "Zoom cận cảnh vào repo header và card thông số kỹ thuật",
                "payoff": "Người xem nhận ra ngay giải pháp chạy AI offline không tốn phí",
                "transition": "Slide to growth metrics"
            }
        elif seg_type == "what_is_it":
            return {
                "visual_type": "DATA_VISUALIZATION",
                "sub_label": "SỐ LIỆU TĂNG TRƯỞNG & CỘNG ĐỒNG TOÀN CẦU",
                "diagram_elements": ["181,800+ STARS", "82.5 TOKENS/S", "4.7GB VRAM", "TOP 1 LOCAL AI"],
                "motion_type": "PUSH_IN",
                "semantic_intent": "Prove Ollama's monumental community traction and local inference speed",
                "visual_claim": "Hơn 181 nghìn ngôi sao GitHub và tốc độ vượt trội trên Apple Silicon / NVIDIA",
                "attention_target": "Thanh chỉ số token/giây và lượng VRAM tiết kiệm",
                "visual_action": "Hiển thị metric cards với thanh progress lấp đầy",
                "payoff": "Khẳng định vị thế công cụ AI cục bộ số một thế giới",
                "transition": "Slide down to CLI technical flow"
            }
        elif seg_type == "how_it_works":
            return {
                "visual_type": "TECHNICAL_FLOW",
                "sub_label": "NGUYÊN LÝ HOẠT ĐỘNG: 1 DÒNG LỆNH CHẠY AI",
                "diagram_elements": ["CLI INVOCATION", "→", "GGUF QUANTIZATION", "→", "GPU LAYER OFFLOAD", "→", "REST API & SHELL"],
                "motion_type": "DATA_FLOW",
                "semantic_intent": "Explain single-command binary workflow without tedious CUDA setups",
                "visual_claim": "Không cần cài đặt phức tạp, tự động lượng tử hóa và offload phần cứng",
                "attention_target": "Sơ đồ 4 bước tự động hóa từ lệnh CLI tới cổng chat",
                "visual_action": "Dòng dữ liệu chạy tuần tự qua các node kiến trúc",
                "payoff": "Hiểu rõ tại sao Ollama dễ dùng vượt trội so với setup truyền thống",
                "transition": "Zoom into API interaction demo"
            }
        elif seg_type in ["interaction_demo", "browser_interaction"]:
            return {
                "visual_type": "BROWSER_DEMO",
                "sub_label": "TƯƠNG TÁCH THỰC TẾ: API CHUẨN OPENAI",
                "diagram_elements": ["POST /v1/chat/completions", "→", "STREAM RESPONSE", "→", "AUTONOMOUS AGENTS"],
                "motion_type": "ZOOM_TO_DETAIL",
                "semantic_intent": "Demonstrate standardized OpenAI-compatible REST API integration with any tool",
                "visual_claim": "Cắm vào LangChain, Autogen, Cursor ngay lập tức mà không cần đổi code",
                "attention_target": "Endpoint localhost:11434 và luồng stream chunking trả về 82 token/s",
                "visual_action": "Hiển thị request JSON và stream response sinh chữ trực tiếp",
                "payoff": "Lập trình viên biết có thể dùng thay thế OpenAI API tức thì",
                "transition": "Zoom to terminal demo"
            }
        elif seg_type == "tech_closeup":
            return {
                "visual_type": "TERMINAL_DEMO",
                "sub_label": "CHI TIẾT KỸ THUẬT: GPU LAYER OFFLOADING",
                "diagram_elements": [
                    "$ ollama run llama3:8b",
                    "offloading 33 repeating layers to GPU",
                    "offloaded 33/33 layers to Metal GPU",
                    ">> eval time = 242ms (82.5 T/s)"
                ],
                "motion_type": "REVEAL",
                "semantic_intent": "Deep dive into Go daemon and C++ llama.cpp backend offloading VRAM layers to GPU",
                "visual_claim": "Tự động đẩy toàn bộ model layer sang Metal hoặc CUDA",
                "attention_target": "Dòng chữ offload 33/33 layers sang GPU và tốc độ 82.5 tokens/s",
                "visual_action": "Cuộn hiển thị log terminal thực tế khi khởi động model",
                "payoff": "Người xem tin tưởng vào năng lực kỹ thuật và hiệu năng thực sự",
                "transition": "Slide to privacy before/after comparison"
            }
        elif seg_type == "why_care":
            return {
                "visual_type": "BEFORE_AFTER",
                "sub_label": "SO SÁNH: CLOUD API TỐN KÉM VS OLLAMA BẢO MẬT",
                "diagram_elements": [
                    "CLOUD API: NGUY CƠ RÒ RỈ & HÀNG NGÀN USD",
                    "VS",
                    "OLLAMA: 0 ĐỒNG & 100% PRIVATE AIR-GAPPED"
                ],
                "motion_type": "BEFORE_AFTER_SPLIT",
                "semantic_intent": "Highlight financial savings and complete source-code confidentiality",
                "visual_claim": "Dữ liệu ở lại máy, chi phí API giảm về 0 tuyệt đối",
                "attention_target": "Bảng so sánh đỏ (rủi ro cloud) và xanh lá (tự chủ cá nhân)",
                "visual_action": "Chia đôi màn hình làm bật lợi thế chi phí 0đ và bảo mật",
                "payoff": "Thúc đẩy người xem tải về dùng ngay cho dự án thực tế",
                "transition": "Push in to payoff visual"
            }
        elif seg_type == "payoff":
            return {
                "visual_type": "PAYOFF_VISUAL",
                "sub_label": "TỰ DO HÓA AI CỤC BỘ",
                "diagram_elements": ["LOCAL AI", "GPU ACCEL", "ZERO COST", "181K STARS"],
                "motion_type": "PAYOFF_PUSH",
                "semantic_intent": "Deliver inspiring conclusion on local AI sovereignty for all developers",
                "visual_claim": "Mỗi lập trình viên đều sở hữu một siêu trí tuệ nhân tạo trên máy",
                "attention_target": "4 trụ cột của Ollama và link repository",
                "visual_action": "Đẩy sâu vào thông điệp tương lai AI thuộc về máy cá nhân",
                "payoff": "Người xem cảm thấy được trao quyền và muốn hành động ngay",
                "transition": "Transition to CTA safe screen"
            }
        else:
            return self._map_general_devtool_beat(seg, seg_type, spoken)

    def _map_browser_use_beat(self, seg, seg_type: str, spoken: str) -> Dict[str, Any]:
        if seg_type == "hook":
            return {
                "visual_type": "REAL_REPOSITORY_UI",
                "sub_label": "TRENDING REPOSITORY // AI BROWSER AGENT",
                "diagram_elements": ["browser-use/browser-use", "32K+ STARS", "PYTHON", "OPEN SOURCE"],
                "motion_type": "ZOOM_TO_DETAIL",
                "semantic_intent": "Establish repository identity and massive developer traction",
                "visual_claim": "browser-use là dự án AI Agent điều khiển trình duyệt số 1",
                "attention_target": "Repo header, 32K+ stars counter, và tên dự án",
                "visual_action": "Zoom cận cảnh vào huy hiệu 32.000 stars và tiêu đề repo",
                "payoff": "Xác thực repo uy tín hàng đầu trên GitHub",
                "transition": "Slide down to architecture flow"
            }
        elif seg_type == "what_is_it":
            return {
                "visual_type": "TECHNICAL_FLOW",
                "sub_label": "KIẾN TRÚC KẾT NỐI AI VỚI TRÌNH DUYỆT",
                "diagram_elements": ["AI AGENT (LLM)", "→", "BROWSER-USE CONTROLLER", "→", "HEADLESS CHROMIUM"],
                "motion_type": "DATA_FLOW",
                "semantic_intent": "Explain how browser-use bridges LLM with the web browser",
                "visual_claim": "Kết nối trực tiếp mô hình AI với trình duyệt web",
                "attention_target": "Mũi tên truyền dữ liệu từ AI Controller vào Chromium DOM",
                "visual_action": "Dòng dữ liệu chạy tuần tự từ LLM sang Browser Controller sang Web DOM",
                "payoff": "Người xem hiểu rõ cơ chế AI điều khiển trình duyệt",
                "transition": "Zoom into simulated browser window"
            }
        elif seg_type in ["how_it_works", "browser_interaction", "interaction_demo"]:
            # If spoken mentions comparison / scraper vs agent
            if "scraper" in spoken or "truyền thống" in spoken or "thay thế" in spoken:
                return {
                    "visual_type": "BEFORE_AFTER",
                    "sub_label": "SO SÁNH: SCRAPER TRUYỀN THỐNG VS BROWSER-USE",
                    "diagram_elements": ["SCRAPER: 500 DÒNG XPATH DỄ GÃY", "VS", "BROWSER-USE: TỰ THÍCH ỨNG BẰNG AI"],
                    "motion_type": "BEFORE_AFTER_SPLIT",
                    "semantic_intent": "Contrast brittle legacy scrapers with resilient autonomous AI agent",
                    "visual_claim": "Không cần viết mã cào dữ liệu thủ công dễ gãy",
                    "attention_target": "Bảng đối chiếu xanh lá (AI tự lành) đối lập với đỏ (lỗi XPath)",
                    "visual_action": "Chia đôi màn hình so sánh lỗi code cũ và giải pháp AI tự hành",
                    "payoff": "Chứng minh sự vượt trội của phương pháp AI mới",
                    "transition": "Pan to live browser demo"
                }
            else:
                return {
                    "visual_type": "BROWSER_DEMO",
                    "sub_label": "MÔ PHỎNG AI TỰ DUYỆT WEB & ĐIỀN FORM",
                    "diagram_elements": ["NAVIGATE: booking.com", "FILL FORM: 'Chuyến bay đi Tokyo'", "CLICK: 'Tìm vé rẻ nhất'"],
                    "motion_type": "PUSH_IN",
                    "semantic_intent": "Demonstrate autonomous browser actions including URL navigation and form submission",
                    "visual_claim": "AI tự mở web, điền thông tin và tương tác y như con người",
                    "attention_target": "Con trỏ chuột ảo đang tự động gõ chữ và click nút tìm kiếm",
                    "visual_action": "Con trỏ di chuyển vào ô input, điền văn bản và bấm submit",
                    "payoff": "Minh chứng trực quan AI thay người dùng duyệt web hoàn chỉnh",
                    "transition": "Pan to terminal execution"
                }
        elif seg_type == "tech_closeup":
            return {
                "visual_type": "TERMINAL_DEMO",
                "sub_label": "MÃ NGUỒN THỰC THI & LOG PARSER",
                "diagram_elements": ["$ pip install browser-use", "Agent(task='Book flight', llm=ChatOpenAI())", ">> DOM Parsed & Action Executed [200 OK]"],
                "motion_type": "REVEAL",
                "semantic_intent": "Show developer implementation code and terminal output",
                "visual_claim": "Cài đặt siêu nhanh chỉ với 3 dòng mã Python đơn giản",
                "attention_target": "Cửa sổ dòng lệnh Terminal hiển thị mã khởi tạo Agent",
                "visual_action": "Hiện dần từng dòng code Python và log kết quả thành công",
                "payoff": "Kỹ sư thấy rõ tính khả thi và dễ tích hợp của thư viện",
                "transition": "Slide to impact metric"
            }
        elif seg_type == "why_care":
            return {
                "visual_type": "DATA_VISUALIZATION",
                "sub_label": "TỐI ƯU HÓA QUY TRÌNH & HIỆU SUẤT",
                "diagram_elements": ["TIẾT KIỆM 95% THỜI GIAN", "TỰ ĐỘNG HÓA 24/7", "KHÔNG CẦN DUY TRÌ SCRIPT"],
                "motion_type": "DATA_FLOW",
                "semantic_intent": "Demonstrate concrete engineering productivity gains",
                "visual_claim": "Tự động hóa hoàn toàn các thao tác web lặp đi lặp lại",
                "attention_target": "Chỉ số 95% thời gian tiết kiệm và biểu đồ năng suất",
                "visual_action": "Thanh đo tiến độ tăng vọt thể hiện hiệu suất nhảy vọt",
                "payoff": "Người xem nhận thức giá trị thực tế cho công việc",
                "transition": "Push in to final payoff"
            }
        elif seg_type == "payoff":
            return {
                "visual_type": "PAYOFF_VISUAL",
                "sub_label": "TƯƠNG LAI CỦA WEB AGENT TỰ HÀNH",
                "diagram_elements": ["TỰ DO HÓA LẬP TRÌNH VIÊN", "LINK: github.com/browser-use/browser-use"],
                "motion_type": "PAYOFF_PUSH",
                "semantic_intent": "Deliver final inspiring synthesis and link to repository",
                "visual_claim": "browser-use mở ra kỷ nguyên mới cho tự động hóa web",
                "attention_target": "Khung tổng kết giải pháp và liên kết GitHub repo",
                "visual_action": "Hiệu ứng zoom đẩy mạnh vào hộp chứng nhận kết quả",
                "payoff": "Đỉnh điểm ấn tượng giúp người xem nhớ dự án",
                "transition": "Transition to CTA safe screen"
            }
        else:
            return self._map_general_devtool_beat(seg, seg_type, spoken)

    def _map_omi_beat(self, seg, seg_type: str, spoken: str) -> Dict[str, Any]:
        if seg_type == "hook":
            return {
                "visual_type": "REAL_REPOSITORY_UI",
                "sub_label": "TRENDING HARDWARE AI // BASED HARDWARE",
                "diagram_elements": ["BasedHardware/omi", "13.5K+ STARS", "WEARABLE AI", "OPEN HARDWARE"],
                "motion_type": "PUSH_IN",
                "semantic_intent": "Introduce Omi wearable AI open hardware project",
                "visual_claim": "Thiết bị AI đeo được mã nguồn mở gây bão cộng đồng",
                "attention_target": "Huy hiệu 13.5K+ Stars và sơ đồ thiết bị Omi",
                "visual_action": "Zoom vào thông số mã nguồn mở và hình dáng thiết bị",
                "payoff": "Nhận diện ngay lập tức phần cứng đột phá",
                "transition": "Slide down"
            }
        elif seg_type == "what_is_it":
            return {
                "visual_type": "TECHNICAL_FLOW",
                "sub_label": "SỐ LIỆU TĂNG TRƯỞNG & ĐỘ HOT GITHUB",
                "diagram_elements": ["13,500+ STARS", "1,400+ FORKS", "OPEN HARDWARE", "MIT LICENSE"],
                "motion_type": "ZOOM_TO_DETAIL",
                "semantic_intent": "Highlight GitHub community traction and open source licensing",
                "visual_claim": "Dự án phần cứng AI hot nhất GitHub hiện nay",
                "attention_target": "Thông số sao và lượt đóng góp cộng đồng",
                "visual_action": "Phóng to số liệu 13.500+ Stars",
                "payoff": "Chứng minh độ nóng thực tế của dự án",
                "transition": "Slide to workflow"
            }
        elif seg_type == "how_it_works":
            return {
                "visual_type": "TECHNICAL_FLOW",
                "sub_label": "KIẾN TRÚC THU ÂM & PHÂN TÍCH THỜI GIAN THỰC",
                "diagram_elements": ["MIC / SENSORS", "→", "AUDIO STREAM", "→", "WHISPER AI", "→", "LLM ACTION"],
                "motion_type": "DATA_FLOW",
                "semantic_intent": "Explain real-time audio perception pipeline",
                "visual_claim": "Liên tục nghe hội thoại và đồng bộ thời gian thực",
                "attention_target": "Luồng tín hiệu âm thanh chuyển hóa thành hành động AI",
                "visual_action": "Các node xử lý kích hoạt theo thứ tự",
                "payoff": "Hiểu rõ cách thiết bị xử lý âm thanh xung quanh",
                "transition": "Pan to mobile UI"
            }
        elif seg_type in ["interaction_demo", "browser_interaction"]:
            return {
                "visual_type": "TECHNICAL_FLOW",
                "sub_label": "MÔ PHỎNG ỨNG DỤNG TỰ ĐỘNG TÓM TẮT CUỘC HỌP",
                "diagram_elements": ["LIVE MEETING", "AI AUTO-SUMMARY", "ACTION ITEMS EXTRACTED"],
                "motion_type": "REVEAL",
                "semantic_intent": "Show mobile app receiving live meeting notes and action items",
                "visual_claim": "Tự động tóm tắt cuộc họp và trích xuất việc cần làm",
                "attention_target": "Thẻ ghi chú tóm tắt và danh sách việc cần làm hoàn thành",
                "visual_action": "Nội dung cuộc họp được phân loại trực quan theo thời gian thực",
                "payoff": "Thấy rõ giá trị thực tiễn trong công việc hàng ngày",
                "transition": "Pan to hardware schematics"
            }
        elif seg_type == "tech_closeup":
            return {
                "visual_type": "ARCHITECTURE_DIAGRAM",
                "sub_label": "THIẾT KẾ MẠCH IN KICAD VÀ FILE 3D IN",
                "diagram_elements": ["KICAD PCB SCHEMATIC", "BLE 5.2 CHIP", "3D PRINT STL", "OPEN FIRMWARE"],
                "motion_type": "ZOOM_TO_DETAIL",
                "semantic_intent": "Show fully open PCB schematics and 3D printing files",
                "visual_claim": "Toàn bộ phần cứng, firmware và mã nguồn đều mở 100%",
                "attention_target": "Sơ đồ mạch in PCB và file thiết kế 3D tải về được",
                "visual_action": "Phóng to các linh kiện phần cứng mã nguồn mở",
                "payoff": "Kỹ sư có thể tự in 3D và hàn mạch tại nhà",
                "transition": "Slide to comparison"
            }
        elif seg_type == "why_care":
            return {
                "visual_type": "BEFORE_AFTER",
                "sub_label": "SO SÁNH: THIẾT BỊ ĐÓNG VS OMI TỰ LÀM",
                "diagram_elements": ["THIẾT BỊ ĐÓNG: KHÓA DỮ LIỆU & ĐẮT", "VS", "OMI: MÃ NGUỒN MỞ & TỰ QUẢN LÝ"],
                "motion_type": "BEFORE_AFTER_SPLIT",
                "semantic_intent": "Compare private self-hosted hardware with costly closed corporate alternatives",
                "visual_claim": "Không lo rò rỉ dữ liệu cá nhân hay chi phí thuê bao",
                "attention_target": "Bảng so sánh bảo mật dữ liệu và quyền tự chủ thiết bị",
                "visual_action": "Chia đôi màn hình làm nổi bật ưu thế bảo mật của Omi",
                "payoff": "Quyết định ủng hộ giải pháp mở bảo vệ riêng tư",
                "transition": "Push in to final payoff"
            }
        elif seg_type == "payoff":
            return {
                "visual_type": "PAYOFF_VISUAL",
                "sub_label": "KỶ NGUYÊN THIẾT BỊ AI ĐEO ĐƯỢC",
                "diagram_elements": ["TRỢ LÝ AI CỦA RIÊNG BẠN", "LINK: github.com/BasedHardware/omi"],
                "motion_type": "PAYOFF_PUSH",
                "semantic_intent": "Conclude with personal AI empowerment takeaway",
                "visual_claim": "Tự tay làm chủ trợ lý AI tương lai",
                "attention_target": "Hộp tổng kết tầm nhìn phần cứng AI mở",
                "visual_action": "Zoom mạnh vào biểu tượng tự chủ công nghệ",
                "payoff": "Truyền cảm hứng tự lắp ráp phần cứng",
                "transition": "Transition to CTA safe screen"
            }
        else:
            return self._map_general_devtool_beat(seg, seg_type, spoken)

    def _map_zed_beat(self, seg, seg_type: str, spoken: str) -> Dict[str, Any]:
        """Semantic beat mapping for Zed editor (AI-native code editor, Rust/GPU, multi-buffer)."""
        if seg_type == "hook":
            return {
                "visual_type": "REAL_REPOSITORY_UI",
                "sub_label": "TRENDING REPOSITORY // AI-NATIVE CODE EDITOR",
                "diagram_elements": ["zed-industries/zed", "58K+ STARS", "RUST", "OPEN SOURCE"],
                "motion_type": "ZOOM_TO_DETAIL",
                "semantic_intent": "Establish Zed as the fastest AI-native code editor — written in Rust, GPU-rendered",
                "visual_claim": "Zed la code editor nhanh nhat the gioi",
                "attention_target": "Ten du an ZED va so sao GitHub",
                "visual_action": "Zoom can canh vao header repo va huy hieu stars",
                "payoff": "Nguoi xem biet ngay day la du an code editor dot pha",
                "transition": "Slide down to metrics beat"
            }
        elif seg_type == "what_is_it":
            return {
                "visual_type": "DATA_VISUALIZATION",
                "sub_label": "SO LIEU TANG TRUONG & HIEU NANG",
                "diagram_elements": ["58K+ STARS", "RENDER < 1ms", "GPU-NATIVE", "MIT LICENSE"],
                "motion_type": "ZOOM_TO_DETAIL",
                "semantic_intent": "Prove Zed's community traction and sub-millisecond render performance",
                "visual_claim": "Zed dat toc do render duoi 1 mili giay va co cong dong khong lo",
                "attention_target": "So sao 58K+ va chi so render < 1ms",
                "visual_action": "Hien thi metric cards voi thanh do",
                "payoff": "Chung minh hieu nang vuot troi bang so lieu thuc te",
                "transition": "Transition to technical flow"
            }
        elif seg_type == "how_it_works":
            return {
                "visual_type": "TECHNICAL_FLOW",
                "sub_label": "KIEN TRUC: RUST + GPUI — KHONG CO ELECTRON",
                "diagram_elements": ["VS CODE (Electron / 200MB RAM)", "VS", "ZED (GPUI Rust / 40MB RAM)"],
                "motion_type": "DATA_FLOW",
                "semantic_intent": "Explain why Zed is fast: Rust + GPU rendering, no Electron overhead",
                "visual_claim": "Zed bo Electron, dung GPUI Rust de render UI tren GPU",
                "attention_target": "So sanh RAM va toc do giua VS Code va Zed",
                "visual_action": "Pipeline Rust → GPUI → GPU Frame Buffer hien thi tuan tu",
                "payoff": "Nguoi xem hieu tai sao Zed nhanh hon — la vi kien truc",
                "transition": "Zoom into AI editor demo"
            }
        elif seg_type in ["interaction_demo", "browser_interaction"]:
            return {
                "visual_type": "BROWSER_DEMO",
                "sub_label": "AI INLINE — CHAT TRONG EDITOR",
                "diagram_elements": ["NATURAL LANGUAGE PROMPT", "→", "AI GENERATE CODE", "→", "INLINE RESULT"],
                "motion_type": "PUSH_IN",
                "semantic_intent": "Show AI-inline code generation: developer types prompt, AI writes code in-place",
                "visual_claim": "AI viet code, refactor va giai thich loi ngay trong cua so soan thao",
                "attention_target": "O chat AI va doan code duoc sinh ra",
                "visual_action": "Go lenh tu nhien, AI tra ve code truc tiep vao file",
                "payoff": "Lap trinh vien khong can roi khoi editor de dung AI",
                "transition": "Zoom to multi-buffer terminal"
            }
        elif seg_type == "tech_closeup":
            return {
                "visual_type": "TERMINAL_DEMO",
                "sub_label": "MULTI-BUFFER EDITING",
                "diagram_elements": [
                    "# Buffer 1: frontend/App.tsx",
                    "# Buffer 2: backend/api.py",
                    "# Buffer 3: infra/deploy.yml",
                    ">> [DONE] 3 files edited simultaneously"
                ],
                "motion_type": "REVEAL",
                "semantic_intent": "Demonstrate multi-buffer editing: multiple files from different repos open simultaneously",
                "visual_claim": "Mo cung luc nhieu file tu cac repo khac nhau, chinh sua dong thoi",
                "attention_target": "3 buffer dang mo dong thoi trong cung mot cua so",
                "visual_action": "Lan luot reveal 3 buffer panels voi code co mau",
                "payoff": "Nguoi xem thay duoc tinh nang ma VS Code va Neovim chua lam duoc",
                "transition": "Slide to benchmark metrics"
            }
        elif seg_type == "why_care":
            return {
                "visual_type": "DATA_VISUALIZATION",
                "sub_label": "BENCHMARK THUC TE: ZED VS VS CODE",
                "diagram_elements": [
                    "KHOI DONG: Zed 0.3s | VS Code 3.1s",
                    "RAM SU DUNG: Zed 40MB | VS Code 200MB",
                    "KEYSTROKE LATENCY: Zed 2ms | VS Code 20ms"
                ],
                "motion_type": "DATA_FLOW",
                "semantic_intent": "Prove with benchmarks: Zed starts 10x faster, uses 5x less RAM",
                "visual_claim": "Zed khoi dong nhanh hon VS Code 10 lan, dung it RAM hon 5 lan",
                "attention_target": "Thanh do so sanh khoi dong va RAM",
                "visual_action": "Thanh benchmark lan luot fill len cho tung chi so",
                "payoff": "Lap trinh vien tiet kiem hang gio moi tuan nho hieu nang tot hon",
                "transition": "Fade to payoff"
            }
        elif seg_type == "payoff":
            return {
                "visual_type": "PAYOFF_VISUAL",
                "sub_label": "TUONG LAI CUA CODE EDITOR",
                "diagram_elements": ["AI-NATIVE", "GPU-RENDERED", "MA NGUON MO", "CONG DONG 58K+"],
                "motion_type": "PAYOFF_PUSH",
                "semantic_intent": "Deliver the big takeaway: AI-native, GPU-rendered open source is the future of code editors",
                "visual_claim": "Tuong lai la AI-native va ma nguon mo — Zed dan dau",
                "attention_target": "4 pillars cua Zed: AI-Native, GPU, Open Source, Community",
                "visual_action": "Push cam giac thanh cong voi 4 card hieu ung payoff",
                "payoff": "Nguoi xem nghi: phai thu Zed ngay",
                "transition": "Transition to CTA"
            }
        else:
            return self._map_general_devtool_beat(seg, seg_type, spoken)

    def _map_general_devtool_beat(self, seg, seg_type: str, spoken: str) -> Dict[str, Any]:

        if seg_type == "hook":
            return {
                "visual_type": "REAL_REPOSITORY_UI",
                "sub_label": "GITHUB REPOSITORY DISCOVERY",
                "diagram_elements": ["REPOSITORY HEADER", "STARS METRIC", "TOPIC TAGS"],
                "motion_type": "PUSH_IN",
                "semantic_intent": "Introduce the repository and spark developer interest",
                "visual_claim": "Dự án mã nguồn mở đáng chú ý trên GitHub",
                "attention_target": "Tên repository và số sao",
                "visual_action": "Zoom vào tiêu đề repo và chỉ số cộng đồng",
                "payoff": "Người xem biết chính xác dự án đang được phân tích",
                "transition": "Slide down"
            }
        elif seg_type == "what_is_it":
            return {
                "visual_type": "DATA_VISUALIZATION",
                "sub_label": "SỐ LIỆU TĂNG TRƯỞNG & CỘNG ĐỒNG",
                "diagram_elements": ["STARS", "FORKS", "CONTRIBUTORS", "LICENSE"],
                "motion_type": "ZOOM_TO_DETAIL",
                "semantic_intent": "Highlight repository popularity and credibility",
                "visual_claim": "Được hàng nghìn lập trình viên tin dùng",
                "attention_target": "Thống kê sao và thông tin giấy phép mở",
                "visual_action": "Phóng to số sao và các chỉ số hoạt động",
                "payoff": "Khẳng định chất lượng của dự án",
                "transition": "Slide to technical flow"
            }
        elif seg_type == "how_it_works":
            return {
                "visual_type": "TECHNICAL_FLOW",
                "sub_label": "SƠ ĐỒ NGUYÊN LÝ HOẠT ĐỘNG",
                "diagram_elements": ["INPUT DATA", "→", "CORE ENGINE", "→", "OPTIMIZED OUTPUT"],
                "motion_type": "DATA_FLOW",
                "semantic_intent": "Show architecture pipeline and execution logic",
                "visual_claim": "Kiến trúc xử lý dữ liệu thông minh và tinh gọn",
                "attention_target": "Luồng dữ liệu di chuyển qua các thành phần cốt lõi",
                "visual_action": "Dòng dữ liệu chạy tuần tự qua các module",
                "payoff": "Nắm vững nguyên lý vận hành kỹ thuật",
                "transition": "Pan to live demo"
            }
        elif seg_type in ["interaction_demo", "browser_interaction"]:
            return {
                "visual_type": "BROWSER_DEMO",
                "sub_label": "MÔ PHỎNG TƯƠNG TÁC THỰC TẾ",
                "diagram_elements": ["INPUT QUERY", "PROCESS TASK", "VERIFIED RESULT"],
                "motion_type": "PUSH_IN",
                "semantic_intent": "Simulate real usage and execution results",
                "visual_claim": "Tự động hóa tác vụ chính xác và nhanh chóng",
                "attention_target": "Giao diện điều khiển và kết quả trả về",
                "visual_action": "Hiển thị tương tác trực tiếp trên giao diện",
                "payoff": "Chứng minh ứng dụng thực tiễn giải quyết bài toán",
                "transition": "Pan to terminal"
            }
        elif seg_type == "tech_closeup":
            return {
                "visual_type": "TERMINAL_DEMO",
                "sub_label": "LỆNH DÒNG VÀ MÃ NGUỒN",
                "diagram_elements": ["$ git clone", "$ run command", ">> Success: 100%"],
                "motion_type": "REVEAL",
                "semantic_intent": "Show terminal implementation and code structure",
                "visual_claim": "Dễ dàng tích hợp vào luồng làm việc hiện tại",
                "attention_target": "Dòng lệnh thực thi trong Terminal",
                "visual_action": "Hiện dần dòng lệnh và log phản hồi thành công",
                "payoff": "Lập trình viên sẵn sàng thử nghiệm ngay",
                "transition": "Slide to comparison"
            }
        elif seg_type == "why_care":
            return {
                "visual_type": "BEFORE_AFTER",
                "sub_label": "SO SÁNH HIỆU QUẢ CÔNG VIỆC",
                "diagram_elements": ["CÁCH CŨ: TỐN THỜI GIAN & PHỨC TẠP", "VS", "CÁCH MỚI: TỰ ĐỘNG & NHANH GẤP 10 LẦN"],
                "motion_type": "BEFORE_AFTER_SPLIT",
                "semantic_intent": "Contrast traditional workflow with modern automated workflow",
                "visual_claim": "Tối ưu hóa hiệu năng và giải phóng thời gian lập trình",
                "attention_target": "Bảng đối chiếu hiệu suất trước và sau khi ứng dụng",
                "visual_action": "Chia đôi màn hình làm bật sự cải thiện hiệu quả",
                "payoff": "Thấy rõ lợi ích năng suất không thể bỏ qua",
                "transition": "Push in to final payoff"
            }
        elif seg_type == "payoff":
            return {
                "visual_type": "PAYOFF_VISUAL",
                "sub_label": "TỔNG KẾT DỰ ÁN ĐỘT PHÁ",
                "diagram_elements": ["GIẢI PHÁP ĐÁNG TRẢI NGHIỆM", "LINK TẢI TRONG MÔ TẢ"],
                "motion_type": "PAYOFF_PUSH",
                "semantic_intent": "Final project synthesis and repository link",
                "visual_claim": "Công cụ đáng giá bổ sung vào bộ vũ khí lập trình",
                "attention_target": "Hộp tổng kết và liên kết GitHub repo",
                "visual_action": "Zoom cận cảnh vào thẻ tổng kết kết quả",
                "payoff": "Khán giả lưu lại dự án để áp dụng",
                "transition": "Transition to CTA safe screen"
            }
        else:
            return {
                "visual_type": "TECHNICAL_FLOW",
                "sub_label": "MINH HỌA KỸ THUẬT",
                "diagram_elements": ["MODULE A", "→", "MODULE B"],
                "motion_type": "DATA_FLOW",
                "semantic_intent": "Technical visualization",
                "visual_claim": "Minh họa kiến trúc hệ thống",
                "attention_target": "Sơ đồ module",
                "visual_action": "Dòng dữ liệu chạy",
                "payoff": "Hiểu rõ logic phần mềm",
                "transition": "Next scene"
            }
