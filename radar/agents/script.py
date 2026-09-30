from typing import Dict, Any, List
from radar.models.schemas import StorySelectionArtifact, ScriptArtifact, ScriptSegment


class ScriptGenerationAgent:
    """Generates structured, high-retention video scripts in conversational Vietnamese,
    tailored dynamically to any selected repository.
    
    Structure:
    0-2s: Strong hook (immediate curiosity & subject identification)
    2-7s: What is this? (clear identity)
    7-15s: How does it work? (technical concept)
    15-25s: Real use / Interaction demo
    25-35s: Why viewers should care (practical engineer payoff)
    35-43s: Surprise reveal / Takeaway
    43-47s: Strict CTA (Like, Share, Subscribe only. No comment CTA).
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.shorts_cfg = config.get("formats", {}).get("shorts", {})
        self.target_duration = self.shorts_cfg.get("target_duration_sec", 45)

    def generate(self, story: StorySelectionArtifact) -> ScriptArtifact:
        repo = story.selected_repos[0]
        repo_data = repo.repository

        stars_k = round(repo_data.stars / 1000, 1)
        stars_str = f"{stars_k} nghìn" if stars_k >= 1 else f"{repo_data.stars}"
        
        # Build repository-specific narrative beats
        if "browser-use" in repo_data.name.lower():
            segments = [
                ScriptSegment(
                    order=1,
                    beat_id="B01_HOOK",
                    segment_type="hook",
                    spoken_text="Công cụ AI biến trình duyệt web thành robot tự động này đang gây bão toàn cầu.",
                    estimated_duration_sec=4.0,
                    visual_type="REAL_REPOSITORY_UI",
                    motion_type="ZOOM_TO_DETAIL",
                    visual_cue="github_repo_header",
                    headline_text=f"{repo_data.name.upper()}",
                    supporting_evidence=[f"Repository {repo_data.full_name}"]
                ),
                ScriptSegment(
                    order=2,
                    beat_id="B02_STAR_COUNT",
                    segment_type="what_is_it",
                    spoken_text=f"Vượt mốc {stars_str} ngôi sao trên GitHub, dự án mang tên {repo_data.name}.",
                    estimated_duration_sec=4.5,
                    visual_type="TECHNICAL_FLOW",
                    motion_type="DATA_FLOW",
                    visual_cue="agent_browser_bridge",
                    headline_text=f"{stars_k}K+ STARS TRÊN GITHUB",
                    supporting_evidence=[f"Stars: {repo_data.stars:,}"]
                ),
                ScriptSegment(
                    order=3,
                    beat_id="B03_HOW_IT_WORKS",
                    segment_type="how_it_works",
                    spoken_text="Khác với scraper truyền thống dễ gãy, AI ở đây tự nhìn màn hình và điều khiển trình duyệt như người thật.",
                    estimated_duration_sec=7.0,
                    visual_type="BEFORE_AFTER",
                    motion_type="BEFORE_AFTER_SPLIT",
                    visual_cue="scraper_vs_agent",
                    headline_text="TỰ NHÌN & TỰ THÍCH ỨNG",
                    supporting_evidence=["Vision-driven DOM extraction"]
                ),
                ScriptSegment(
                    order=4,
                    beat_id="B04_INTERACTION_DEMO",
                    segment_type="interaction_demo",
                    spoken_text="Chỉ cần ra lệnh bằng lời nói, AI sẽ tự động mở web, tìm chuyến bay rẻ nhất và điền form hoàn chỉnh.",
                    estimated_duration_sec=7.5,
                    visual_type="BROWSER_DEMO",
                    motion_type="PUSH_IN",
                    visual_cue="flight_search_automation",
                    headline_text="TỰ ĐỘNG ĐIỀN FORM VÀ CLICK",
                    supporting_evidence=["Playwright DOM click automation"]
                ),
                ScriptSegment(
                    order=5,
                    beat_id="B05_TECH_CLOSEUP",
                    segment_type="tech_closeup",
                    spoken_text="Được viết bằng Python, anh em có thể tích hợp thư viện này vào dự án chỉ với 3 dòng mã đơn giản.",
                    estimated_duration_sec=6.5,
                    visual_type="TERMINAL_DEMO",
                    motion_type="REVEAL",
                    visual_cue="python_agent_code",
                    headline_text="CÀI ĐẶT 3 DÒNG PYTHON",
                    supporting_evidence=[repo_data.language]
                ),
                ScriptSegment(
                    order=6,
                    beat_id="B06_WHY_CARE",
                    segment_type="why_care",
                    spoken_text="Nó giúp lập trình viên tiết kiệm đến 95 phần trăm thời gian viết mã cào dữ liệu và tự động hóa.",
                    estimated_duration_sec=6.5,
                    visual_type="DATA_VISUALIZATION",
                    motion_type="DATA_FLOW",
                    visual_cue="productivity_gains",
                    headline_text="TIẾT KIỆM 95% THỜI GIAN",
                    supporting_evidence=["95% automation efficiency"]
                ),
                ScriptSegment(
                    order=7,
                    beat_id="B07_PAYOFF",
                    segment_type="payoff",
                    spoken_text=f"Một dự án đột phá anh em bắt buộc phải thử. Đường dẫn repo {repo_data.name} có ở mô tả video.",
                    estimated_duration_sec=6.0,
                    visual_type="PAYOFF_VISUAL",
                    motion_type="PAYOFF_PUSH",
                    visual_cue="project_payoff_summary",
                    headline_text="KỶ NGUYÊN WEB AGENT MỚI",
                    supporting_evidence=[repo.takeaway]
                ),
                ScriptSegment(
                    order=8,
                    beat_id="B08_CTA",
                    segment_type="cta",
                    spoken_text="Nếu thấy video hữu ích, hãy like, share và đăng ký kênh nhé.",
                    estimated_duration_sec=4.0,
                    visual_type="CTA",
                    motion_type="PUSH_IN",
                    visual_cue="cta_safe_screen",
                    headline_text="LIKE • SHARE • ĐĂNG KÝ",
                    supporting_evidence=["Strict CTA Policy: Like, Share, Subscribe only"]
                )
            ]
            title = f"{repo_data.name}: Biến AI Thành Robot Tự Duyệt Web Gây Sốt Toàn Cầu"
        elif "omi" in repo_data.name.lower():
            segments = [
                ScriptSegment(
                    order=1,
                    beat_id="B01_HOOK",
                    segment_type="hook",
                    spoken_text="Thiết bị AI mã nguồn mở này đang khiến giới công nghệ phát sốt.",
                    estimated_duration_sec=3.5,
                    visual_type="REAL_REPOSITORY_UI",
                    motion_type="PUSH_IN",
                    visual_cue="wearable_ai_necklace",
                    headline_text=f"{repo_data.name.upper()}",
                    supporting_evidence=[f"Repository {repo_data.full_name}"]
                ),
                ScriptSegment(
                    order=2,
                    beat_id="B02_STAR_COUNT",
                    segment_type="what_is_it",
                    spoken_text=f"Vừa vượt mốc {stars_str} ngôi sao trên GitHub, dự án mang tên {repo_data.name}.",
                    estimated_duration_sec=5.0,
                    visual_type="TECHNICAL_FLOW",
                    motion_type="ZOOM_TO_DETAIL",
                    visual_cue="github_metrics",
                    headline_text=f"{stars_k}K+ STARS TRÊN GITHUB",
                    supporting_evidence=[f"Stars: {repo_data.stars:,}"]
                ),
                ScriptSegment(
                    order=3,
                    beat_id="B03_HOW_IT_WORKS",
                    segment_type="how_it_works",
                    spoken_text="Cách hoạt động rất ấn tượng: Thiết bị liên tục nghe hội thoại, nhìn màn hình và đồng bộ thời gian thực.",
                    estimated_duration_sec=7.5,
                    visual_type="TECHNICAL_FLOW",
                    motion_type="DATA_FLOW",
                    visual_cue="audio_transcription_pipeline",
                    headline_text="NGHE HỘI THOẠI & NHÌN MÀN HÌNH",
                    supporting_evidence=["Audio transcription + Screen vision"]
                ),
                ScriptSegment(
                    order=4,
                    beat_id="B04_INTERACTION_DEMO",
                    segment_type="interaction_demo",
                    spoken_text="Từ tự động tóm tắt cuộc họp, nhắc nhở công việc cho đến phân tích hành động theo thời gian thực.",
                    estimated_duration_sec=7.5,
                    visual_type="TECHNICAL_FLOW",
                    motion_type="REVEAL",
                    visual_cue="wearable_meeting_summary",
                    headline_text="TỰ TÓM TẮT & GỢI Ý 24/7",
                    supporting_evidence=["Live summary & proactive assistance"]
                ),
                ScriptSegment(
                    order=5,
                    beat_id="B05_TECH_CLOSEUP",
                    segment_type="tech_closeup",
                    spoken_text="Điểm đặc biệt nhất là toàn bộ phần cứng, firmware và mã nguồn AI đều mở hoàn toàn.",
                    estimated_duration_sec=6.5,
                    visual_type="ARCHITECTURE_DIAGRAM",
                    motion_type="ZOOM_TO_DETAIL",
                    visual_cue="pcb_firmware_open_source",
                    headline_text="PHẦN CỨNG & CODE MỞ 100%",
                    supporting_evidence=["Open Hardware + Open Source"]
                ),
                ScriptSegment(
                    order=6,
                    beat_id="B06_WHY_CARE",
                    segment_type="why_care",
                    spoken_text="Thay vì mua những thiết bị đắt đỏ và bị khóa dữ liệu, anh em có thể tự lắp ráp và sở hữu AI của riêng mình.",
                    estimated_duration_sec=7.5,
                    visual_type="BEFORE_AFTER",
                    motion_type="BEFORE_AFTER_SPLIT",
                    visual_cue="private_vs_closed_ai",
                    headline_text="BẢO MẬT • KHÔNG PHỤ THUỘC",
                    supporting_evidence=[repo.why_care]
                ),
                ScriptSegment(
                    order=7,
                    beat_id="B07_PAYOFF",
                    segment_type="payoff",
                    spoken_text=f"AI cá nhân đang bước ra đời thực. Link repo {repo_data.name} có ở mô tả video.",
                    estimated_duration_sec=6.0,
                    visual_type="PAYOFF_VISUAL",
                    motion_type="PAYOFF_PUSH",
                    visual_cue="future_wearable_ai",
                    headline_text="LÀN SÓNG AI ĐEO ĐƯỢC",
                    supporting_evidence=[repo.takeaway]
                ),
                ScriptSegment(
                    order=8,
                    beat_id="B08_CTA",
                    segment_type="cta",
                    spoken_text="Nếu thấy video hữu ích, hãy like, share và đăng ký kênh nhé.",
                    estimated_duration_sec=4.0,
                    visual_type="CTA",
                    motion_type="PUSH_IN",
                    visual_cue="cta_safe_screen",
                    headline_text="LIKE • SHARE • ĐĂNG KÝ",
                    supporting_evidence=["Strict CTA Policy: Like, Share, Subscribe only"]
                )
            ]
            title = f"{repo_data.name}: Thiết Bị AI Đeo Được Mã Nguồn Mở Gây Sốt Toàn Cầu"
        elif "zed" in repo_data.name.lower():
            segments = [
                ScriptSegment(
                    order=1,
                    beat_id="B01_HOOK",
                    segment_type="hook",
                    spoken_text="Code editor nhanh nhất thế giới — viết bằng Rust, render bằng GPU — vừa mở mã nguồn và đang gây bão cộng đồng lập trình.",
                    estimated_duration_sec=4.5,
                    visual_type="REAL_REPOSITORY_UI",
                    motion_type="ZOOM_TO_DETAIL",
                    visual_cue="github_repo_header",
                    headline_text="ZED EDITOR",
                    supporting_evidence=[f"Repository {repo_data.full_name}"]
                ),
                ScriptSegment(
                    order=2,
                    beat_id="B02_STAR_COUNT",
                    segment_type="what_is_it",
                    spoken_text=f"Vượt mốc {stars_str} ngôi sao chỉ trong thời gian ngắn — Zed là editor AI-native đầu tiên đạt tốc độ render dưới 1 mili giây.",
                    estimated_duration_sec=5.0,
                    visual_type="DATA_VISUALIZATION",
                    motion_type="ZOOM_TO_DETAIL",
                    visual_cue="github_metrics",
                    headline_text=f"{stars_k}K+ STARS TRÊN GITHUB",
                    supporting_evidence=[f"Stars: {repo_data.stars:,}"]
                ),
                ScriptSegment(
                    order=3,
                    beat_id="B03_HOW_IT_WORKS",
                    segment_type="how_it_works",
                    spoken_text="Bí quyết: Zed không dùng Electron như VS Code — toàn bộ UI render trực tiếp trên GPU bằng GPUI framework viết bằng Rust.",
                    estimated_duration_sec=6.5,
                    visual_type="TECHNICAL_FLOW",
                    motion_type="DATA_FLOW",
                    visual_cue="rust_gpu_render_pipeline",
                    headline_text="RUST + GPU RENDER",
                    supporting_evidence=["GPUI framework, no Electron overhead"]
                ),
                ScriptSegment(
                    order=4,
                    beat_id="B04_INTERACTION_DEMO",
                    segment_type="interaction_demo",
                    spoken_text="AI tích hợp sẵn trong editor — gõ lệnh tự nhiên, AI viết code, refactor, giải thích lỗi ngay trong cửa sổ soạn thảo.",
                    estimated_duration_sec=7.0,
                    visual_type="BROWSER_DEMO",
                    motion_type="PUSH_IN",
                    visual_cue="zed_ai_inline_demo",
                    headline_text="AI INLINE — KHÔNG CẦN PLUGIN",
                    supporting_evidence=["Built-in LLM: Claude, GPT-4, local models"]
                ),
                ScriptSegment(
                    order=5,
                    beat_id="B05_TECH_CLOSEUP",
                    segment_type="tech_closeup",
                    spoken_text="Multi-buffer editing: mở cùng lúc nhiều file từ các repo khác nhau, chỉnh sửa đồng thời — điều VS Code và Neovim chưa làm được.",
                    estimated_duration_sec=6.5,
                    visual_type="TERMINAL_DEMO",
                    motion_type="REVEAL",
                    visual_cue="multi_buffer_editing",
                    headline_text="MULTI-BUFFER EDITING",
                    supporting_evidence=["Multi-file simultaneous editing"]
                ),
                ScriptSegment(
                    order=6,
                    beat_id="B06_WHY_CARE",
                    segment_type="why_care",
                    spoken_text="Benchmark thực tế: Zed khởi động nhanh hơn VS Code 10 lần, dùng ít RAM hơn 5 lần — lập trình viên tiết kiệm hàng giờ mỗi tuần.",
                    estimated_duration_sec=6.5,
                    visual_type="DATA_VISUALIZATION",
                    motion_type="DATA_FLOW",
                    visual_cue="performance_benchmarks",
                    headline_text="NHANH HON VS CODE 10 LAN",
                    supporting_evidence=["10x startup speed, 5x less RAM"]
                ),
                ScriptSegment(
                    order=7,
                    beat_id="B07_PAYOFF",
                    segment_type="payoff",
                    spoken_text=f"Tương lai của code editor là AI-native, GPU-rendered và mã nguồn mở. Link repo Zed có ở mô tả video.",
                    estimated_duration_sec=5.5,
                    visual_type="PAYOFF_VISUAL",
                    motion_type="PAYOFF_PUSH",
                    visual_cue="ai_editor_future",
                    headline_text="TUONG LAI CUA CODE EDITOR",
                    supporting_evidence=[repo.takeaway]
                ),
                ScriptSegment(
                    order=8,
                    beat_id="B08_CTA",
                    segment_type="cta",
                    spoken_text="Nếu thấy video hữu ích, hãy like, share và đăng ký kênh nhé.",
                    estimated_duration_sec=4.0,
                    visual_type="CTA",
                    motion_type="PUSH_IN",
                    visual_cue="cta_safe_screen",
                    headline_text="LIKE • SHARE • ĐĂNG KÝ",
                    supporting_evidence=["Strict CTA Policy: Like, Share, Subscribe only"]
                )
            ]
            title = f"Zed: Code Editor AI-Native Nhanh Nhất Thế Giới — Viết Bằng Rust, Render Bằng GPU"
        elif "ollama" in repo_data.name.lower():
            segments = [
                ScriptSegment(
                    order=1,
                    beat_id="B01_HOOK",
                    segment_type="hook",
                    spoken_text="Chạy Llama 3 và DeepSeek mượt mà ngay trên laptop mà không tốn một đồng API hay gửi dữ liệu ra ngoài?",
                    estimated_duration_sec=4.0,
                    visual_type="REAL_REPOSITORY_UI",
                    motion_type="ZOOM_TO_DETAIL",
                    visual_cue="github_repo_header",
                    headline_text="OLLAMA LOCAL AI",
                    supporting_evidence=[f"Repository {repo_data.full_name}"]
                ),
                ScriptSegment(
                    order=2,
                    beat_id="B02_STAR_COUNT",
                    segment_type="what_is_it",
                    spoken_text=f"Vừa cán mốc hơn {stars_str} ngôi sao GitHub, Ollama đang là công cụ số một để đưa AI về máy cá nhân.",
                    estimated_duration_sec=4.5,
                    visual_type="DATA_VISUALIZATION",
                    motion_type="PUSH_IN",
                    visual_cue="github_metrics",
                    headline_text=f"{stars_str.upper()} SAO GITHUB",
                    supporting_evidence=[f"Stars: {repo_data.stars:,}"]
                ),
                ScriptSegment(
                    order=3,
                    beat_id="B03_HOW_IT_WORKS",
                    segment_type="how_it_works",
                    spoken_text="Không cần cấu hình CUDA phức tạp. Chỉ cần một dòng lệnh duy nhất, Ollama tự động tải trọng số, lượng tử hóa GGUF và mở cổng chat.",
                    estimated_duration_sec=7.0,
                    visual_type="TECHNICAL_FLOW",
                    motion_type="DATA_FLOW",
                    visual_cue="tech_pipeline",
                    headline_text="1 DÒNG LỆNH CHẠY AI",
                    supporting_evidence=["Single binary runtime"]
                ),
                ScriptSegment(
                    order=4,
                    beat_id="B04_INTERACTION_DEMO",
                    segment_type="interaction_demo",
                    spoken_text="Giao diện OpenAI REST API chuẩn hóa giúp anh em kết nối ngay lập tức với bất kỳ ứng dụng hoặc agent tự hành nào.",
                    estimated_duration_sec=6.5,
                    visual_type="BROWSER_DEMO",
                    motion_type="ZOOM_TO_DETAIL",
                    visual_cue="speed_benchmark_demo",
                    headline_text="API CHUẨN OPENAI",
                    supporting_evidence=["OpenAI compatible API endpoints"]
                ),
                ScriptSegment(
                    order=5,
                    beat_id="B05_TECH_CLOSEUP",
                    segment_type="tech_closeup",
                    spoken_text="Backend tối ưu bằng Go và C++ tự động offload các layer sang GPU Metal hoặc CUDA, đạt tốc độ trên 80 token mỗi giây.",
                    estimated_duration_sec=6.5,
                    visual_type="TERMINAL_DEMO",
                    motion_type="REVEAL",
                    visual_cue="code_terminal",
                    headline_text="GPU LAYER OFFLOADING",
                    supporting_evidence=["Metal / CUDA hardware offload"]
                ),
                ScriptSegment(
                    order=6,
                    beat_id="B06_WHY_CARE",
                    segment_type="why_care",
                    spoken_text="Không còn hóa đơn cloud hàng nghìn đô, không lo rò rỉ mã nguồn mật. Dữ liệu của anh em ở lại máy của anh em.",
                    estimated_duration_sec=6.5,
                    visual_type="BEFORE_AFTER",
                    motion_type="BEFORE_AFTER_SPLIT",
                    visual_cue="productivity_diagram",
                    headline_text="BẢO MẬT • TIẾT KIỆM 100%",
                    supporting_evidence=["Air-gapped on-premise execution"]
                ),
                ScriptSegment(
                    order=7,
                    beat_id="B07_PAYOFF",
                    segment_type="payoff",
                    spoken_text=f"Đưa quyền năng AI về tay lập trình viên. Link repo Ollama mình để ngay ở phần mô tả.",
                    estimated_duration_sec=5.0,
                    visual_type="PAYOFF_VISUAL",
                    motion_type="PAYOFF_PUSH",
                    visual_cue="project_payoff_summary",
                    headline_text="TỰ DO HÓA AI CỤC BỘ",
                    supporting_evidence=[repo.takeaway]
                ),
                ScriptSegment(
                    order=8,
                    beat_id="B08_CTA",
                    segment_type="cta",
                    spoken_text="Thấy hữu ích thì like, share và đăng ký kênh để đón xem siêu phẩm tiếp theo nhé!",
                    estimated_duration_sec=4.0,
                    visual_type="CTA",
                    motion_type="PUSH_IN",
                    visual_cue="cta_safe_screen",
                    headline_text="LIKE • SHARE • ĐĂNG KÝ",
                    supporting_evidence=["Strict CTA Policy: Like, Share, Subscribe only"]
                )
            ]
            title = f"Ollama: Chạy Mô Hình AI Local Cực Mượt Trên Mọi Laptop — 181K Sao GitHub"
        else:
            # Universal fallback for general tools
            segments = [
                ScriptSegment(
                    order=1,
                    beat_id="B01_HOOK",
                    segment_type="hook",
                    spoken_text=f"Repo này đang thay đổi hoàn toàn cách giới lập trình làm việc mỗi ngày.",
                    estimated_duration_sec=3.5,
                    visual_type="REAL_REPOSITORY_UI",
                    motion_type="PUSH_IN",
                    visual_cue="tech_concept_icon",
                    headline_text=f"{repo_data.name.upper()}",
                    supporting_evidence=[f"Repository {repo_data.full_name}"]
                ),
                ScriptSegment(
                    order=2,
                    beat_id="B02_STAR_COUNT",
                    segment_type="what_is_it",
                    spoken_text=f"Vừa vượt mốc {stars_str} ngôi sao trên GitHub, dự án mang tên {repo_data.name}.",
                    estimated_duration_sec=5.0,
                    visual_type="DATA_VISUALIZATION",
                    motion_type="ZOOM_TO_DETAIL",
                    visual_cue="github_metrics",
                    headline_text=f"{stars_k}K+ STARS TRÊN GITHUB",
                    supporting_evidence=[f"Stars: {repo_data.stars:,}"]
                ),
                ScriptSegment(
                    order=3,
                    beat_id="B03_HOW_IT_WORKS",
                    segment_type="how_it_works",
                    spoken_text=f"Cách hoạt động: {repo.unusual_capability}",
                    estimated_duration_sec=7.5,
                    visual_type="TECHNICAL_FLOW",
                    motion_type="DATA_FLOW",
                    visual_cue="tech_pipeline",
                    headline_text="CÔNG NGHỆ ĐỘT PHÁ MỚI",
                    supporting_evidence=[repo.unusual_capability]
                ),
                ScriptSegment(
                    order=4,
                    beat_id="B04_INTERACTION_DEMO",
                    segment_type="interaction_demo",
                    spoken_text=f"Xử lý tác vụ với tốc độ vượt trội và kiến trúc tối ưu hóa hoàn toàn.",
                    estimated_duration_sec=7.5,
                    visual_type="BROWSER_DEMO",
                    motion_type="PUSH_IN",
                    visual_cue="speed_benchmark_demo",
                    headline_text="HIỆU NĂNG VƯỢT TRỘI",
                    supporting_evidence=["Architecture benchmarks"]
                ),
                ScriptSegment(
                    order=5,
                    beat_id="B05_TECH_CLOSEUP",
                    segment_type="tech_closeup",
                    spoken_text=f"Được viết bằng {repo_data.language} giúp loại bỏ hoàn toàn các điểm nghẽn hiệu năng.",
                    estimated_duration_sec=6.5,
                    visual_type="TERMINAL_DEMO",
                    motion_type="REVEAL",
                    visual_cue="code_terminal",
                    headline_text=f"TỐI ƯU BẰNG {repo_data.language.upper()}",
                    supporting_evidence=[repo_data.language]
                ),
                ScriptSegment(
                    order=6,
                    beat_id="B06_WHY_CARE",
                    segment_type="why_care",
                    spoken_text=f"Tại sao anh em nên quan tâm? {repo.why_care}",
                    estimated_duration_sec=7.5,
                    visual_type="BEFORE_AFTER",
                    motion_type="BEFORE_AFTER_SPLIT",
                    visual_cue="productivity_diagram",
                    headline_text="TIẾT KIỆM HÀNG TRĂM GIỜ",
                    supporting_evidence=[repo.why_care]
                ),
                ScriptSegment(
                    order=7,
                    beat_id="B07_PAYOFF",
                    segment_type="payoff",
                    spoken_text=f"Một dự án rất đáng để thử. Link repo {repo_data.name} có ở mô tả.",
                    estimated_duration_sec=6.0,
                    visual_type="PAYOFF_VISUAL",
                    motion_type="PAYOFF_PUSH",
                    visual_cue="project_link_screen",
                    headline_text="DỰ ÁN ĐÁNG TRẢI NGHIỆM",
                    supporting_evidence=[repo.takeaway]
                ),
                ScriptSegment(
                    order=8,
                    beat_id="B08_CTA",
                    segment_type="cta",
                    spoken_text="Nếu thấy video hữu ích, hãy like, share và đăng ký kênh nhé.",
                    estimated_duration_sec=4.0,
                    visual_type="CTA",
                    motion_type="PUSH_IN",
                    visual_cue="cta_safe_screen",
                    headline_text="LIKE • SHARE • ĐĂNG KÝ",
                    supporting_evidence=["Strict CTA Policy: Like, Share, Subscribe only"]
                )
            ]
            title = f"{repo_data.name}: Dự Án Mã Nguồn Mở Đột Phá Đang Gây Sốt"

        total_words = sum(len(s.spoken_text.split()) for s in segments)
        description = (
            f"Khám phá dự án mã nguồn mở cực hot: {repo_data.name}\n"
            f"GitHub: {repo_data.html_url}\n\n"
            f"Số sao: {repo_data.stars:,} | Ngôn ngữ: {repo_data.language}\n"
            f"Mô tả: {repo_data.description}\n\n"
            f"#github #laptrinh #congnghe #opensource #ai #developer"
        )
        tags = ["github", "laptrinh", "congnghe", "opensource", repo_data.name.lower(), (repo_data.language or "tech").lower()]

        return ScriptArtifact(
            story_id=story.story_id,
            format=story.format,
            language="vi",
            title=title,
            description=description,
            tags=tags,
            hook=segments[0].spoken_text,
            target_duration_sec=round(sum(s.estimated_duration_sec for s in segments), 1),
            total_spoken_words=total_words,
            segments=segments
        )
