import os
import uuid
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont
from radar.models.schemas import VisualStoryboard, VisualBeatEvent
from radar.utils.ai_image_generator import build_beat_prompt, fetch_ai_image
from radar.utils.real_tech_visuals import get_real_tech_visual


class AssetGenerationAgent:
    """Generates rich, high-contrast, technical visual scene assets in 1080x1920 vertical format.
    
    Implements Visual Storytelling Engine V3:
    Renders exact UI/DOM interactions, forms, flows, cursors, terminals, and architectures
    matching the narration claims:
    - REAL_REPOSITORY_UI: GitHub repo header, star counter, tags, commit stats
    - TECHNICAL_FLOW: Node pipeline showing data transformations with connecting arrows
    - BROWSER_DEMO: Simulated web browser, URL bar, form inputs, active cursor clicking
    - TERMINAL_DEMO: Command-line terminal shell, code snippet, and execution log output
    - ARCHITECTURE_DIAGRAM: Component blocks, protocol interfaces, data buses
    - BEFORE_AFTER: Side-by-side comparison (Brittle Legacy vs Resilient AI)
    - DATA_VISUALIZATION: Performance benchmarks, metric cards, progress bars
    - PAYOFF_VISUAL: Inspiring takeaway synthesis card with repository link
    - CTA: Strict policy-compliant call to action (Like • Share • Đăng ký kênh)
    """

    def __init__(self, config: Dict[str, Any], output_dir: str = "data/visuals"):
        self.config = config
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        shorts_cfg = config.get("formats", {}).get("shorts", {})
        self.width = shorts_cfg.get("width", 1080)
        self.height = shorts_cfg.get("height", 1920)
        self.use_ai_visuals = config.get("visuals", {}).get("use_ai_visuals", True)
        self.font_path = "/Library/Fonts/Arial Unicode.ttf"
        if not os.path.exists(self.font_path):
            self.font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

    def generate_assets(self, storyboard: VisualStoryboard) -> VisualStoryboard:
        rendered_paths = []
        for beat in storyboard.beats:
            path = self._render_beat_asset(beat, storyboard.repo_category)
            beat.asset_path = path
            rendered_paths.append(path)

        storyboard.rendered_assets = rendered_paths
        return storyboard

    def _render_beat_asset(self, beat: VisualBeatEvent, repo_category: str = "DEV_TOOL") -> str:
        out_path = os.path.join(self.output_dir, f"{beat.beat_id}.png")

        # 1. Base Canvas - Deep tech dark slate theme
        img = Image.new("RGB", (self.width, self.height), color=(10, 14, 23))
        draw = ImageDraw.Draw(img)

        # Fonts
        f_badge = self._font(24)
        f_headline = self._font(50)
        f_sub = self._font(28)
        f_node = self._font(32)
        f_code = self._font(28)
        f_small = self._font(22)

        # 2. Header Top Bar & Badge (Top 120px to 320px)
        draw.rectangle([(0, 0), (self.width, 16)], fill=(14, 165, 233))

        # Badge: GitHub Radar Identity
        badge_y = 120
        draw.rectangle([(80, badge_y), (1000, badge_y + 60)], fill=(20, 30, 48), outline=(37, 99, 235), width=2)
        draw.text((105, badge_y + 14), "GITHUB PROJECT RADAR // TECH DISCOVERY", font=f_badge, fill=(56, 189, 248))

        # Primary Visual Headline (<= 6 words, bold, vibrant)
        headline_y = 210
        draw.text((80, headline_y), beat.headline_text, font=f_headline, fill=(255, 255, 255))
        
        # Sub-label / narrative context
        draw.text((80, headline_y + 75), beat.sub_label, font=f_sub, fill=(148, 163, 184))

        # Determine repo_full_name from beat context
        all_text = " ".join(beat.diagram_elements) + " " + beat.headline_text + " " + beat.sub_label
        if "zed" in all_text.lower():
            repo_full_name = "zed-industries/zed"
        elif "omi" in all_text.lower():
            repo_full_name = "BasedHardware/omi"
        elif "ollama" in all_text.lower():
            repo_full_name = "ollama/ollama"
        elif "uv" in all_text.lower():
            repo_full_name = "astral-sh/uv"
        else:
            repo_full_name = "browser-use/browser-use"

        # 3. Dynamic Center Technical Canvas (y: 360 to 1540)
        card_t = 360
        card_b = 1540
        ai_rendered = False

        if self.use_ai_visuals and beat.visual_type.upper() != "CTA":
            real_img = get_real_tech_visual(beat, repo_full_name=repo_full_name, width=960, height=card_b - card_t)
            if real_img:
                img.paste(real_img, (60, card_t))
                draw.rectangle([(60, card_t), (1020, card_b)], outline=(56, 189, 248), width=3)
                self._draw_window_header(draw, card_t, f"tech_preview // {beat.visual_type.lower()}")
                ai_rendered = True

        if not ai_rendered:
            draw.rectangle([(60, card_t), (1020, card_b)], fill=(16, 23, 38), outline=(51, 65, 85), width=3)

            v_type = beat.visual_type.upper()

            if v_type in ["REAL_REPOSITORY_UI", "REPOSITORY_HOOK", "STAR_COUNT_HOOK"]:
                self._draw_repo_ui(draw, beat, card_t, f_node, f_sub)
            elif v_type in ["TECHNICAL_FLOW", "AGENT_WORKFLOW"]:
                self._draw_technical_flow(draw, beat, card_t, f_node, f_sub)
            elif v_type in ["BROWSER_DEMO", "BROWSER_INTERACTION", "DEVICE_INTERACTION"]:
                self._draw_browser_demo(draw, beat, card_t, f_node, f_sub)
            elif v_type in ["TERMINAL_DEMO", "CODE_VISUALIZATION"]:
                self._draw_terminal_demo(draw, beat, card_t, f_node, f_sub, f_code)
            elif v_type in ["ARCHITECTURE_DIAGRAM", "SYSTEM_DIAGRAM", "HARDWARE_VISUALIZATION"]:
                self._draw_architecture_diagram(draw, beat, card_t, f_node, f_sub)
            elif v_type == "BEFORE_AFTER":
                self._draw_before_after(draw, beat, card_t, f_node, f_sub)
            elif v_type == "DATA_VISUALIZATION":
                self._draw_data_visualization(draw, beat, card_t, f_node, f_sub)
            elif v_type in ["PAYOFF_VISUAL", "RESULT_PAYOFF"]:
                self._draw_payoff_visual(draw, beat, card_t, f_node, f_sub)
            elif v_type == "CTA":
                self._draw_cta(draw, card_t, f_headline, f_node)
            elif v_type == "CHAPTER_TITLE_CARD":
                self._draw_chapter_title_card(draw, beat, card_t, f_headline, f_node, f_sub)
            else:
                self._draw_technical_flow(draw, beat, card_t, f_node, f_sub)

        # 4. Spoken Narration Subtitle Box (Safe zone y: 1560 to 1740)
        if beat.narration:
            draw.rectangle([(60, 1560), (1020, 1720)], fill=(15, 23, 42), outline=(37, 99, 235), width=2)
            # Wrap narration into 2 lines
            words = beat.narration.split()
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            draw.text((90, 1585), line1, font=self._font(26), fill=(241, 245, 249))
            if line2:
                draw.text((90, 1635), line2, font=self._font(26), fill=(56, 189, 248))

        # 5. Footer & Disclosure (Safe zone y: 1750 to 1840)
        notice_y = 1750
        draw.text((80, notice_y), beat.synthetic_notice, font=f_small, fill=(100, 116, 139))
        draw.text((80, notice_y + 36), "AUTONOMOUS PRODUCTION • GITHUB PROJECT RADAR V2", font=f_small, fill=(71, 85, 105))

        img.save(out_path, "PNG")
        return out_path

    def _draw_repo_ui(self, draw: ImageDraw.Draw, beat: VisualBeatEvent, top: int, f_node, f_sub):
        self._draw_window_header(draw, top, "github.com/repository-overview")
        
        # Determine repo name
        all_text = " ".join(beat.diagram_elements) + " " + beat.headline_text
        if "zed" in all_text.lower() or "zed-industries" in all_text.lower():
            repo_title = "zed-industries / zed"
            stars_text = "★ 58,200 STARS"
            desc_text = "Code at the speed of thought."
            metrics = [
                ("NGON NGU", "RUST (100% SAFE RUST)"),
                ("RENDER", "GPU-NATIVE / GPUI FRAMEWORK"),
                ("AI", "BUILT-IN LLM: CLAUDE, GPT-4, LOCAL"),
                ("XU HUONG", "TRENDING #1 DEVELOPER TOOLS")
            ]
        elif any("omi" in el.lower() for el in beat.diagram_elements) or "omi" in beat.headline_text.lower():
            repo_title = "BasedHardware / omi"
            stars_text = "★ 13,590 STARS"
            desc_text = "The world's leading open-source AI wearable."
            metrics = [
                ("TIEU CHUAN", "OPEN HARDWARE + MIT LICENSE"),
                ("PHAN CUNG", "ESP32 + MICROPHONE ARRAY"),
                ("AI", "REAL-TIME TRANSCRIPTION + MEMORY"),
                ("XU HUONG", "TRENDING #1 WEARABLE AI")
            ]
        elif "ollama" in all_text.lower():
            repo_title = "ollama / ollama"
            stars_text = "★ 181,800 STARS"
            desc_text = "Get up and running with large language models locally."
            metrics = [
                ("NGÔN NGỮ", "GO + C++ (LLAMA.CPP BACKEND)"),
                ("HIỆU NĂNG", "GPU LAYER OFFLOADING (METAL / CUDA)"),
                ("GIAO TIẾP", "OPENAI-COMPATIBLE REST API (:11434)"),
                ("XU HƯỚNG", "TRENDING #1 LOCAL AI IN THE WORLD")
            ]
        else:
            repo_title = "browser-use / browser-use"
            stars_text = "★ 32,450 STARS"
            desc_text = "Make websites accessible to AI agents."
            metrics = [
                ("TIEU CHUAN", "OPEN SOURCE MIT LICENSE"),
                ("NGON NGU", "PYTHON 3.11+ • ASYNCIO"),
                ("KIEN TRUC", "HEADLESS BROWSER + LLM AGENT"),
                ("XU HUONG", "TRENDING #1 GLOBAL GITHUB")
            ]

        # Repo Card Header
        draw.rectangle([(100, top + 100), (980, top + 360)], fill=(30, 41, 59), outline=(59, 130, 246), width=3)
        draw.text((140, top + 130), repo_title, font=self._font(42), fill=(56, 189, 248))
        draw.text((140, top + 200), desc_text, font=f_sub, fill=(203, 213, 225))
        
        # Star Badge Highlight (Attention Target)
        draw.rectangle([(140, top + 260), (560, top + 330)], fill=(234, 179, 8))
        draw.text((160, top + 275), stars_text, font=self._font(34), fill=(15, 23, 42))

        # Metrics Grid
        y_curr = top + 410
        for label, val in metrics:
            draw.rectangle([(100, y_curr), (980, y_curr + 120)], fill=(23, 32, 48), outline=(51, 65, 85), width=2)
            draw.text((140, y_curr + 25), label, font=f_sub, fill=(148, 163, 184))
            draw.text((140, y_curr + 65), val, font=f_node, fill=(241, 245, 249))
            y_curr += 150

    def _draw_technical_flow(self, draw: ImageDraw.Draw, beat: VisualBeatEvent, top: int, f_node, f_sub):
        # Determine window label and steps from context
        all_text = " ".join(beat.diagram_elements) + " " + beat.headline_text
        is_ollama = "ollama" in all_text.lower() or "gguf" in all_text.lower() or "dòng lệnh" in all_text.lower()
        is_zed = ("zed" in all_text.lower() or "gpui" in all_text.lower()) and not is_ollama

        if is_ollama:
            window_label = "ollama_local_runtime.flow"
            steps = [
                ("1. SINGLE CLI INVOCATION", "$ ollama run llama3:8b (Tự động pull trọng số)", (59, 130, 246)),
                ("2. GGUF QUANTIZATION & DAEMON", "Quản lý VRAM thông minh • K-quants (Q4_K_M)", (16, 185, 129)),
                ("3. HARDWARE ACCELERATION", "Offload toàn bộ layers sang Apple Metal / NVIDIA CUDA", (168, 85, 247)),
                ("4. REST API & INTERACTIVE SHELL", "Localhost:11434 mở sẵn • Tốc độ 80+ tokens/giây", (245, 158, 11))
            ]
        elif is_zed:
            window_label = "zed_architecture.flow"
            colors = [(239, 68, 68), (37, 99, 235), (16, 185, 129)]
            steps = [
                ("ELECTRON APPROACH (VS CODE)", "200MB RAM • 3s startup • JS overhead", (239, 68, 68)),
                ("ZED: RUST + GPUI FRAMEWORK", "40MB RAM • 0.3s startup • GPU render", (37, 99, 235)),
                ("GPU FRAME BUFFER OUTPUT", "Render < 1ms • Keystroke latency 2ms", (16, 185, 129)),
            ]
        elif beat.diagram_elements and len(beat.diagram_elements) >= 3:
            window_label = "autonomous_agent_pipeline.flow"
            palette = [(59, 130, 246), (16, 185, 129), (168, 85, 247), (245, 158, 11)]
            steps = []
            for i, el in enumerate(beat.diagram_elements[:4]):
                if el.strip() in ["→", "VS", ""]:
                    continue
                color = palette[len(steps) % len(palette)]
                steps.append((el, "", color))
        else:
            window_label = "autonomous_agent_pipeline.flow"
            steps = [
                ("1. LLM AGENT PROMPT", "Muc tieu: 'Mo web, tim ve may bay re nhat'", (59, 130, 246)),
                ("2. BROWSER-USE CONTROLLER", "Trich xuat DOM cay & chup anh man hinh", (16, 185, 129)),
                ("3. CHROMIUM EXECUTION", "Tu dong go phim, click button & cuon trang", (168, 85, 247)),
                ("4. PAYOFF OUTPUT", "Lay du lieu da loc tra ve nguoi dung hoan tat", (245, 158, 11))
            ]

        self._draw_window_header(draw, top, window_label)
        y_curr = top + 100
        for i, step_data in enumerate(steps):
            if len(step_data) == 3:
                title, desc, color = step_data
            else:
                title, color = step_data[0], (59, 130, 246)
                desc = ""
            draw.rectangle([(100, y_curr), (980, y_curr + 160)], fill=(24, 32, 47), outline=color, width=3)
            draw.rectangle([(100, y_curr), (120, y_curr + 160)], fill=color)
            draw.text((140, y_curr + 25), title, font=f_node, fill=(255, 255, 255))
            if desc:
                draw.text((140, y_curr + 85), desc, font=f_sub, fill=(203, 213, 225))
            # Flow arrow if not last
            if i < len(steps) - 1:
                draw.text((530, y_curr + 175), "▼", font=self._font(28), fill=(56, 189, 248))
                y_curr += 225
            else:
                y_curr += 180

    def _draw_browser_demo(self, draw: ImageDraw.Draw, beat: VisualBeatEvent, top: int, f_node, f_sub):
        all_text = " ".join(beat.diagram_elements) + " " + beat.headline_text
        is_zed = "zed" in all_text.lower() or "ai inline" in all_text.lower() or "chat trong" in all_text.lower() or "inline" in all_text.lower()

        if is_zed:
            # Zed AI inline editor demo
            self._draw_window_header(draw, top, "zed — project/src/main.rs (AI inline)")
            page_t = top + 90

            # Code editor area (dark background)
            draw.rectangle([(100, page_t), (980, page_t + 950)], fill=(13, 17, 23))

            # File tabs
            draw.rectangle([(100, page_t), (980, page_t + 50)], fill=(22, 27, 34))
            draw.rectangle([(100, page_t), (280, page_t + 50)], fill=(30, 41, 59), outline=(59, 130, 246), width=1)
            draw.text((120, page_t + 14), "main.rs", font=self._font(24), fill=(56, 189, 248))
            draw.text((300, page_t + 14), "lib.rs", font=self._font(24), fill=(100, 116, 139))
            draw.text((420, page_t + 14), "Cargo.toml", font=self._font(24), fill=(100, 116, 139))

            # Code lines
            code_lines = [
                ("1", "use zed::prelude::*;", (148, 163, 184)),
                ("2", "", (148, 163, 184)),
                ("3", "fn render_frame(ctx: &AppContext) {", (241, 245, 249)),
                ("4", "    // TODO: optimize GPU path", (100, 116, 139)),
                ("5", "    ctx.gpu_render(|frame| {", (241, 245, 249)),
                ("6", "        frame.draw_text(\"Hello\")", (244, 114, 182)),
                ("7", "    })", (241, 245, 249)),
                ("8", "}", (241, 245, 249)),
            ]
            y_code = page_t + 70
            for lnum, line, color in code_lines:
                draw.text((120, y_code), lnum, font=self._font(22), fill=(71, 85, 105))
                draw.text((160, y_code), line, font=self._font(22), fill=color)
                y_code += 42

            # AI chat prompt box
            ai_t = page_t + 450
            draw.rectangle([(100, ai_t), (980, ai_t + 50)], fill=(30, 41, 59))
            draw.text((130, ai_t + 14), "AI ASSISTANT (Ctrl+Enter)", font=self._font(22), fill=(56, 189, 248))

            draw.rectangle([(100, ai_t + 55), (980, ai_t + 145)], fill=(22, 27, 34), outline=(59, 130, 246), width=2)
            draw.text((130, ai_t + 75), "> Refactor render_frame to use async/await", font=self._font(24), fill=(244, 114, 182))

            # AI response inline
            draw.rectangle([(100, ai_t + 160), (980, ai_t + 450)], fill=(17, 24, 39), outline=(16, 185, 129), width=2)
            draw.text((130, ai_t + 180), "AI GENERATING CODE...", font=self._font(22), fill=(52, 211, 153))
            ai_code = [
                "async fn render_frame(ctx: &AppContext) {",
                "    ctx.gpu_render_async(|frame| async {",
                "        frame.draw_text(\"Hello\").await",
                "    }).await",
                "}",
            ]
            y_ai = ai_t + 220
            for line in ai_code:
                draw.text((140, y_ai), line, font=self._font(22), fill=(241, 245, 249))
                y_ai += 40

            draw.rectangle([(100, ai_t + 490), (980, ai_t + 540)], fill=(5, 46, 22))
            draw.text((130, ai_t + 507), "[OK] Code generated inline — no plugin needed", font=self._font(24), fill=(52, 211, 153))

        elif "ollama" in all_text.lower() or "api" in all_text.lower():
            self._draw_window_header(draw, top, "HTTP Client — localhost:11434/api/chat (OpenAI Format)")
            page_t = top + 90
            draw.rectangle([(100, page_t), (980, page_t + 950)], fill=(13, 17, 23))

            # HTTP Request Box
            draw.rectangle([(100, page_t), (980, page_t + 50)], fill=(22, 27, 34))
            draw.text((120, page_t + 14), "POST http://localhost:11434/v1/chat/completions", font=self._font(22), fill=(52, 211, 153))

            req_json = [
                "{",
                '  "model": "llama3:8b",',
                '  "messages": [{"role": "user", "content": "Tối ưu thuật toán này"}],',
                '  "stream": true',
                "}"
            ]
            y_r = page_t + 70
            for l in req_json:
                draw.text((140, y_r), l, font=self._font(22), fill=(148, 163, 184))
                y_r += 32

            # Live Stream Response Box
            draw.rectangle([(100, page_t + 250), (980, page_t + 300)], fill=(30, 41, 59))
            draw.text((120, page_t + 264), "HTTP/1.1 200 OK — text/event-stream (82.4 tokens/s)", font=self._font(22), fill=(56, 189, 248))

            stream_lines = [
                'data: {"choices": [{"delta": {"content": "Để "}}]}',
                'data: {"choices": [{"delta": {"content": "tối "}}]}',
                'data: {"choices": [{"delta": {"content": "ưu, "}}]}',
                'data: {"choices": [{"delta": {"content": "chúng ta dùng dynamic programming..."}}]}',
                'data: [DONE]'
            ]
            y_s = page_t + 320
            for l in stream_lines:
                draw.text((140, y_s), l, font=self._font(22), fill=(244, 114, 182))
                y_s += 32

            # App Compatibility Footer
            draw.rectangle([(100, page_t + 510), (980, page_t + 620)], fill=(18, 38, 30), outline=(34, 197, 94), width=2)
            draw.text((130, page_t + 530), "[OK] TƯƠNG THÍCH HOÀN TOÀN MỌI FRAMEWORK AI", font=f_node, fill=(74, 222, 128))
            draw.text((130, page_t + 575), "LangChain • LlamaIndex • Autogen • Open WebUI • Cursor", font=f_sub, fill=(226, 232, 240))

        else:
            self._draw_window_header(draw, top, "Chromium Browser (Automated by AI)")
            # Browser URL Address Bar
            draw.rectangle([(100, top + 90), (980, top + 170)], fill=(30, 41, 59), outline=(71, 85, 105), width=2)
            draw.text((130, top + 115), "URL: https://booking.com/flights/search", font=f_sub, fill=(52, 211, 153))

            page_t = top + 200
            draw.rectangle([(100, page_t), (980, page_t + 850)], fill=(248, 250, 252))
            draw.rectangle([(100, page_t), (980, page_t + 110)], fill=(15, 23, 42))
            draw.text((140, page_t + 35), "BOOKING FLIGHT SEARCH ENGINE", font=f_node, fill=(255, 255, 255))

            draw.text((140, page_t + 150), "DIEM KHOI HANH (ORIGIN):", font=self._font(24), fill=(100, 116, 139))
            draw.rectangle([(140, page_t + 190), (940, page_t + 270)], fill=(255, 255, 255), outline=(59, 130, 246), width=2)
            draw.text((170, page_t + 215), "Ha Noi (HAN) — San bay Noi Bai", font=f_sub, fill=(15, 23, 42))

            draw.text((140, page_t + 300), "DIEM DEN (DESTINATION):", font=self._font(24), fill=(100, 116, 139))
            draw.rectangle([(140, page_t + 340), (940, page_t + 420)], fill=(255, 255, 255), outline=(16, 185, 129), width=3)
            draw.text((170, page_t + 365), "Tokyo (HND) [AI DANG NHAP...|]", font=f_sub, fill=(16, 185, 129))

            btn_t = page_t + 470
            draw.rectangle([(140, btn_t), (940, btn_t + 100)], fill=(37, 99, 235))
            draw.text((360, btn_t + 30), "TIM CHUYEN BAY (SUBMIT)", font=f_node, fill=(255, 255, 255))

            draw.polygon([(780, btn_t + 40), (810, btn_t + 110), (760, btn_t + 85)], fill=(239, 68, 68))
            draw.text((820, btn_t + 45), "AI CLICK", font=self._font(26), fill=(239, 68, 68))

            draw.rectangle([(100, page_t + 620), (980, page_t + 720)], fill=(241, 245, 249), outline=(203, 213, 225), width=2)
            draw.text((140, page_t + 655), "[OK] Trang thai: AI vua hoan thanh dien form va click tu dong", font=f_sub, fill=(5, 150, 105))


    def _draw_terminal_demo(self, draw: ImageDraw.Draw, beat: VisualBeatEvent, top: int, f_node, f_sub, f_code):
        all_text = " ".join(beat.diagram_elements) + " " + beat.headline_text
        is_zed = "zed" in all_text.lower() or "buffer" in all_text.lower() or "rust" in all_text.lower()

        if is_zed:
            self._draw_window_header(draw, top, "zed — multi-buffer editing")
            draw.rectangle([(100, top + 90), (980, top + 1100)], fill=(15, 23, 42))
            lines = [
                ("# ZED MULTI-BUFFER EDITOR", (234, 179, 8)),
                ("# ==============================", (71, 85, 105)),
                ("", (255, 255, 255)),
                ("# Buffer 1: frontend/App.tsx", (56, 189, 248)),
                ("export default function App() {", (241, 245, 249)),
                ("  return <Dashboard data={props} />", (244, 114, 182)),
                ("}", (241, 245, 249)),
                ("", (255, 255, 255)),
                ("# Buffer 2: backend/api.py", (52, 211, 153)),
                ("async def get_data(user_id: str):", (241, 245, 249)),
                ("    return await db.fetch(user_id)", (244, 114, 182)),
                ("", (255, 255, 255)),
                ("# Buffer 3: infra/deploy.yml", (168, 85, 247)),
                ("services:", (241, 245, 249)),
                ("  app: {image: myapp:latest}", (244, 114, 182)),
                ("", (255, 255, 255)),
                (">> [DONE] 3 files edited simultaneously", (250, 204, 21)),
                (">> [OK] All changes saved across repos", (52, 211, 153)),
            ]
        elif "ollama" in all_text.lower() or "offload" in all_text.lower() or "gpu" in all_text.lower() or "layer" in all_text.lower():
            self._draw_window_header(draw, top, "zsh — ollama run llama3:8b (Metal GPU Offload)")
            draw.rectangle([(100, top + 90), (980, top + 1050)], fill=(15, 23, 42))
            lines = [
                ("$ ollama run llama3:8b", (241, 245, 249)),
                ("pulling manifest: 100% [====================]", (56, 189, 248)),
                ("verifying sha256 digest: success", (52, 211, 153)),
                ("", (255, 255, 255)),
                ("# BACKEND INITIALIZATION & HARDWARE ACCEL", (234, 179, 8)),
                ("llm_load_print_meta: format = GGUF V3 (little endian)", (148, 163, 184)),
                ("llm_load_print_meta: arch   = llama", (148, 163, 184)),
                ("llm_load_tensors: offloading 33 repeating layers to GPU", (244, 114, 182)),
                ("llm_load_tensors: offloaded 33/33 layers to Metal GPU", (52, 211, 153)),
                ("llm_load_tensors: VRAM used = 4,680 MB (Metal)", (250, 204, 21)),
                ("", (255, 255, 255)),
                (">>> Chào bạn! Tôi đang chạy 100% offline trên máy bạn.", (255, 255, 255)),
                ("", (255, 255, 255)),
                (">> eval time =   242.31 ms / 20 tokens (82.54 T/s)", (52, 211, 153)),
                (">> total time =  312.18 ms (Zero cloud latency)", (56, 189, 248)),
            ]
        else:
            self._draw_window_header(draw, top, "bash — python -m browser_use.agent")
            draw.rectangle([(100, top + 90), (980, top + 1000)], fill=(15, 23, 42))
            lines = [
                ("$ pip install browser-use langchain-openai", (148, 163, 184)),
                (">> Installed successfully (v0.1.25)", (52, 211, 153)),
                ("", (255, 255, 255)),
                ("# 1. KHOI TAO AGENT THONG MINH", (234, 179, 8)),
                ("from browser_use import Agent", (56, 189, 248)),
                ("from langchain_openai import ChatOpenAI", (56, 189, 248)),
                ("", (255, 255, 255)),
                ("agent = Agent(", (241, 245, 249)),
                ("    task='Tim chuyen bay re nhat Tokyo',", (244, 114, 182)),
                ("    llm=ChatOpenAI(model='gpt-4o')", (241, 245, 249)),
                (")", (241, 245, 249)),
                ("history = await agent.run()", (16, 185, 129)),
                ("", (255, 255, 255)),
                (">> [INFO] Browser started in headless mode", (100, 116, 139)),
                (">> [ACTION] Navigate to booking.com -> 200 OK", (52, 211, 153)),
                (">> [DONE] Ket qua: 3 ve re nhat da luu file!", (250, 204, 21))
            ]

        y_curr = top + 120
        for text, color in lines:
            if text:
                draw.text((130, y_curr), text, font=f_code, fill=color)
            y_curr += 48

    def _draw_architecture_diagram(self, draw: ImageDraw.Draw, beat: VisualBeatEvent, top: int, f_node, f_sub):
        self._draw_window_header(draw, top, "system_architecture_spec.dia")
        
        draw.rectangle([(100, top + 100), (980, top + 320)], fill=(30, 41, 59), outline=(59, 130, 246), width=3)
        draw.text((140, top + 130), "LAYER 1: PERCEPTION & VISION", font=f_node, fill=(56, 189, 248))
        draw.text((140, top + 190), "DOM Tree Parser • Visual Screenshot Overlay", font=f_sub, fill=(203, 213, 225))
        draw.text((140, top + 245), "Trích xuất từng nút bấm, ô input thành danh mục phần tử", font=self._font(24), fill=(148, 163, 184))

        draw.text((530, top + 345), "▼", font=self._font(30), fill=(56, 189, 248))

        draw.rectangle([(100, top + 400), (980, top + 620)], fill=(30, 41, 59), outline=(16, 185, 129), width=3)
        draw.text((140, top + 430), "LAYER 2: REASONING & DECISION", font=f_node, fill=(74, 222, 128))
        draw.text((140, top + 490), "LLM Planner • Self-Healing Loop", font=f_sub, fill=(203, 213, 225))
        draw.text((140, top + 545), "Tự động đổi chiến lược khi gặp popup hoặc captcha", font=self._font(24), fill=(148, 163, 184))

        draw.text((530, top + 645), "▼", font=self._font(30), fill=(16, 185, 129))

        draw.rectangle([(100, top + 700), (980, top + 920)], fill=(30, 41, 59), outline=(245, 158, 11), width=3)
        draw.text((140, top + 730), "LAYER 3: PLAYWRIGHT CONTROLLER", font=f_node, fill=(251, 191, 36))
        draw.text((140, top + 790), "Direct Browser WebSocket Execution", font=f_sub, fill=(203, 213, 225))
        draw.text((140, top + 845), "Tương tác thực tế với trình duyệt không để lại dấu vết", font=self._font(24), fill=(148, 163, 184))

    def _draw_before_after(self, draw: ImageDraw.Draw, beat: VisualBeatEvent, top: int, f_node, f_sub):
        all_text = " ".join(beat.diagram_elements).lower() + " " + beat.headline_text.lower()
        self._draw_window_header(draw, top, "workflow_comparison.view")

        if "ollama" in all_text or "cloud" in all_text or "tiết kiệm" in all_text or "bảo mật" in all_text:
            # Red / Cloud API Leaks & Costs
            draw.rectangle([(100, top + 100), (980, top + 480)], fill=(38, 20, 25), outline=(239, 68, 68), width=3)
            draw.text((140, top + 130), "[X] CLOUD API TRUYỀN THỐNG (OPENAI / ANTHROPIC)", font=f_node, fill=(248, 113, 113))
            draw.text((140, top + 200), "• Tốn hàng ngàn USD tiền API token mỗi tháng", font=f_sub, fill=(226, 232, 240))
            draw.text((140, top + 265), "• Nguy cơ rò rỉ mã nguồn & dữ liệu nhạy cảm ra ngoài", font=f_sub, fill=(226, 232, 240))
            draw.text((140, top + 330), "• Phụ thuộc Internet, rate limit & downtime máy chủ", font=f_sub, fill=(226, 232, 240))
            draw.text((140, top + 395), "• Độ trễ mạng cao (500ms - 2s / request)", font=f_sub, fill=(248, 113, 113))

            draw.text((520, top + 510), "VS", font=self._font(40), fill=(148, 163, 184))

            # Green / Local Ollama Privacy
            draw.rectangle([(100, top + 580), (980, top + 960)], fill=(18, 38, 30), outline=(34, 197, 94), width=3)
            draw.text((140, top + 610), "[OK] OLLAMA: CHẠY AI CỤC BỘ 100% PRIVATE", font=f_node, fill=(74, 222, 128))
            draw.text((140, top + 680), "• Chi phí API: HOÀN TOÀN 0 ĐỒNG (Miễn phí mãi mãi)", font=f_sub, fill=(226, 232, 240))
            draw.text((140, top + 745), "• Dữ liệu tuyệt đối ở lại máy cá nhân, air-gapped an toàn", font=f_sub, fill=(226, 232, 240))
            draw.text((140, top + 810), "• Hoạt động offline mượt mà không cần mạng Internet", font=f_sub, fill=(226, 232, 240))
            draw.text((140, top + 875), "• Tốc độ cực nhanh với GPU Metal/CUDA", font=f_sub, fill=(74, 222, 128))
        else:
            # Red / Brittle Legacy Side
            draw.rectangle([(100, top + 100), (980, top + 480)], fill=(38, 20, 25), outline=(239, 68, 68), width=3)
            draw.text((140, top + 130), "[X] WEB SCRAPER TRUYỀN THỐNG (CŨ)", font=f_node, fill=(248, 113, 113))
            draw.text((140, top + 200), "• Viết hàng trăm dòng XPath, Regex thủ công", font=f_sub, fill=(226, 232, 240))
            draw.text((140, top + 265), "• Website đổi giao diện là code lập tức gãy vỡ", font=f_sub, fill=(226, 232, 240))
            draw.text((140, top + 330), "• Tốn hàng chục giờ sửa mã lỗi mỗi tuần", font=f_sub, fill=(226, 232, 240))
            draw.text((140, top + 395), "• Không thể vượt qua form động hay popup", font=f_sub, fill=(248, 113, 113))

            draw.text((520, top + 510), "VS", font=self._font(40), fill=(148, 163, 184))

            # Green / Autonomous AI Side
            draw.rectangle([(100, top + 580), (980, top + 960)], fill=(18, 38, 30), outline=(34, 197, 94), width=3)
            draw.text((140, top + 610), "[OK] BROWSER-USE: AI AGENT TỰ HÀNH", font=f_node, fill=(74, 222, 128))
            draw.text((140, top + 680), "• Ra lệnh bằng ngôn ngữ tự nhiên đơn giản", font=f_sub, fill=(226, 232, 240))
            draw.text((140, top + 745), "• AI tự nhìn màn hình & tự thích ứng khi web đổi", font=f_sub, fill=(226, 232, 240))
            draw.text((140, top + 810), "• Tiết kiệm 95% thời gian viết mã cào dữ liệu", font=f_sub, fill=(226, 232, 240))
            draw.text((140, top + 875), "• Tự động hóa hoàn toàn từ đầu đến cuối", font=f_sub, fill=(74, 222, 128))

    def _draw_data_visualization(self, draw: ImageDraw.Draw, beat: VisualBeatEvent, top: int, f_node, f_sub):
        all_text = " ".join(beat.diagram_elements).lower() + " " + beat.headline_text.lower()
        is_zed = "zed" in all_text or "khoi dong" in all_text or "benchmark" in all_text or "58k" in all_text or "render" in all_text

        if is_zed:
            self._draw_window_header(draw, top, "performance_benchmarks.metrics")
            # Zed vs VS Code benchmark cards
            benchmarks = [
                ("KHOI DONG / STARTUP TIME", "Zed: 0.3s   VS Code: 3.1s", (52, 211, 153), 0.9),
                ("RAM SU DUNG", "Zed: 40MB   VS Code: 200MB", (56, 189, 248), 0.8),
                ("KEYSTROKE LATENCY", "Zed: 2ms   VS Code: 20ms", (251, 191, 36), 0.95),
            ]
            y_curr = top + 100
            for label, val, color, fill_ratio in benchmarks:
                draw.rectangle([(100, y_curr), (980, y_curr + 280)], fill=(30, 41, 59), outline=color, width=3)
                draw.text((140, y_curr + 30), label, font=f_sub, fill=(148, 163, 184))
                draw.text((140, y_curr + 90), val, font=self._font(38), fill=color)
                # Progress bar: Zed portion
                bar_w = int(840 * fill_ratio)
                draw.rectangle([(140, y_curr + 190), (940, y_curr + 235)], fill=(15, 23, 42))
                draw.rectangle([(140, y_curr + 190), (140 + bar_w, y_curr + 235)], fill=color)
                y_curr += 320
        elif "ollama" in all_text or "sao github" in all_text or "181k" in all_text or "token" in all_text:
            self._draw_window_header(draw, top, "ollama_runtime_benchmarks.metrics")
            benchmarks = [
                ("TỐC ĐỘ SINH TOKEN (APPLE M3 MAX)", "82.5 tokens/s   (Cloud: 42 tokens/s)", (52, 211, 153), 0.92),
                ("DUNG LƯỢNG VRAM (Q4_K_M QUANT)", "4.7 GB VRAM   (FP16 Gốc: 16.0 GB)", (56, 189, 248), 0.85),
                ("CỘNG ĐỒNG TOÀN CẦU (GITHUB)", "181,800+ Stars   (Top 1 Local AI)", (251, 191, 36), 0.98),
            ]
            y_curr = top + 100
            for label, val, color, fill_ratio in benchmarks:
                draw.rectangle([(100, y_curr), (980, y_curr + 280)], fill=(30, 41, 59), outline=color, width=3)
                draw.text((140, y_curr + 30), label, font=f_sub, fill=(148, 163, 184))
                draw.text((140, y_curr + 90), val, font=self._font(38), fill=color)
                bar_w = int(840 * fill_ratio)
                draw.rectangle([(140, y_curr + 190), (940, y_curr + 235)], fill=(15, 23, 42))
                draw.rectangle([(140, y_curr + 190), (140 + bar_w, y_curr + 235)], fill=color)
                y_curr += 320
        else:
            self._draw_window_header(draw, top, "productivity_benchmarks.metrics")
            # High impact metric card 1
            draw.rectangle([(100, top + 100), (980, top + 380)], fill=(30, 41, 59), outline=(16, 185, 129), width=3)
            draw.text((140, top + 130), "TIET KIEM THOI GIAN LAP TRINH", font=f_sub, fill=(148, 163, 184))
            draw.text((140, top + 190), "95% GIAM THIEU MA BAO TRI", font=self._font(44), fill=(52, 211, 153))
            draw.rectangle([(140, top + 290), (940, top + 330)], fill=(15, 23, 42))
            draw.rectangle([(140, top + 290), (900, top + 330)], fill=(16, 185, 129))

            draw.rectangle([(100, top + 420), (980, top + 700)], fill=(30, 41, 59), outline=(59, 130, 246), width=3)
            draw.text((140, top + 450), "TU DONG HOA TAC VU WEB", font=f_sub, fill=(148, 163, 184))
            draw.text((140, top + 510), "24/7 HOAT DONG LIEN TUC", font=self._font(44), fill=(56, 189, 248))
            draw.rectangle([(140, top + 610), (940, top + 650)], fill=(15, 23, 42))
            draw.rectangle([(140, top + 610), (940, top + 650)], fill=(59, 130, 246))

            draw.rectangle([(100, top + 740), (980, top + 980)], fill=(30, 41, 59), outline=(245, 158, 11), width=3)
            draw.text((140, top + 770), "KHA NANG TICH HOP HE THONG", font=f_sub, fill=(148, 163, 184))
            draw.text((140, top + 830), "CHI 3 DONG MA PYTHON", font=self._font(44), fill=(251, 191, 36))
            draw.text((140, top + 910), "Tuong thich OpenAI, Anthropic, DeepSeek, Local Ollama", font=self._font(24), fill=(203, 213, 225))


    def _draw_payoff_visual(self, draw: ImageDraw.Draw, beat: VisualBeatEvent, top: int, f_node, f_sub):
        all_text = " ".join(beat.diagram_elements).lower() + " " + beat.headline_text.lower()
        is_ollama = "ollama" in all_text or "cục bộ" in all_text or "quyền năng" in all_text or "181k" in all_text
        is_zed = ("zed" in all_text or "tuong lai" in all_text or "ai-native" in all_text or "gpui" in all_text) and not is_ollama

        self._draw_window_header(draw, top, "future_tech_summary.vision")

        if is_ollama:
            draw.rectangle([(100, top + 120), (980, top + 520)], fill=(30, 41, 59), outline=(147, 51, 234), width=4)
            draw.text((140, top + 160), "TỰ DO HÓA TRÍ TUỆ NHÂN TẠO", font=self._font(44), fill=(192, 132, 252))
            draw.text((140, top + 260), "Không phụ thuộc Big Tech. Không lo lắng rò rỉ dữ liệu.", font=f_node, fill=(255, 255, 255))
            draw.text((140, top + 340), "Mỗi lập trình viên đều sở hữu một siêu AI trên máy.", font=f_node, fill=(250, 204, 21))
            draw.text((140, top + 420), "Cộng đồng 181K+ Stars chứng minh tương lai là Local AI!", font=f_sub, fill=(52, 211, 153))

            draw.rectangle([(100, top + 580), (980, top + 860)], fill=(23, 32, 48), outline=(59, 130, 246), width=3)
            draw.text((140, top + 630), "GITHUB REPOSITORY LINK:", font=f_sub, fill=(148, 163, 184))
            draw.text((140, top + 695), "github.com/ollama/ollama", font=self._font(36), fill=(56, 189, 248))
            draw.text((140, top + 775), "Đường dẫn chi tiết nằm ngay tại phần mô tả video!", font=f_sub, fill=(203, 213, 225))

            pillars = [("LOCAL AI", (192, 132, 252)), ("GPU ACCEL", (56, 189, 248)),
                       ("ZERO COST", (52, 211, 153)), ("181K STARS", (251, 191, 36))]
            px = 140
            for i, (p_label, p_color) in enumerate(pillars):
                draw.rectangle([(px, top + 940), (px + 190, top + 1040)], fill=(24, 32, 47), outline=p_color, width=2)
                draw.text((px + 15, top + 968), p_label, font=self._font(22), fill=p_color)
                px += 210
        elif is_zed:
            draw.rectangle([(100, top + 120), (980, top + 520)], fill=(30, 41, 59), outline=(147, 51, 234), width=4)
            draw.text((140, top + 160), "TUONG LAI CUA CODE EDITOR", font=self._font(44), fill=(192, 132, 252))
            draw.text((140, top + 260), "AI-native, GPU-rendered, ma nguon mo hoan toan.", font=f_node, fill=(255, 255, 255))
            draw.text((140, top + 340), "Zed dang dan dau cuoc cach mang editor moi.", font=f_node, fill=(250, 204, 21))
            draw.text((140, top + 420), "Cong dong 58K+ dev va tang truong manh!", font=f_sub, fill=(52, 211, 153))

            draw.rectangle([(100, top + 580), (980, top + 860)], fill=(23, 32, 48), outline=(59, 130, 246), width=3)
            draw.text((140, top + 630), "GITHUB REPOSITORY:", font=f_sub, fill=(148, 163, 184))
            draw.text((140, top + 695), "github.com/zed-industries/zed", font=self._font(36), fill=(56, 189, 248))
            draw.text((140, top + 775), "Link chi tiet o phan mo ta video!", font=f_sub, fill=(203, 213, 225))

            # 4 pillars
            pillars = [("AI-NATIVE", (192, 132, 252)), ("GPU RENDER", (56, 189, 248)),
                       ("OPEN SOURCE", (52, 211, 153)), ("58K STARS", (251, 191, 36))]
            px = 140
            for i, (p_label, p_color) in enumerate(pillars):
                draw.rectangle([(px, top + 940), (px + 190, top + 1040)], fill=(24, 32, 47), outline=p_color, width=2)
                draw.text((px + 15, top + 968), p_label, font=self._font(22), fill=p_color)
                px += 210
        else:
            draw.rectangle([(100, top + 120), (980, top + 520)], fill=(30, 41, 59), outline=(147, 51, 234), width=4)
            draw.text((140, top + 160), "TU DO HOA LAP TRINH VIEN", font=self._font(46), fill=(192, 132, 252))
            draw.text((140, top + 260), "Khong con lang phi hang gio cho cong viec thu cong.", font=f_node, fill=(255, 255, 255))
            draw.text((140, top + 340), "AI Agent tu hanh mo ra ky nguyen moi cua Internet.", font=f_node, fill=(250, 204, 21))
            draw.text((140, top + 420), "Mot du an dot pha anh em bat buoc phai thu ngay!", font=f_sub, fill=(52, 211, 153))

            draw.rectangle([(100, top + 580), (980, top + 860)], fill=(23, 32, 48), outline=(59, 130, 246), width=3)
            draw.text((140, top + 630), "GITHUB REPOSITORY LINK:", font=f_sub, fill=(148, 163, 184))
            draw.text((140, top + 695), "github.com/browser-use/browser-use", font=self._font(36), fill=(56, 189, 248))
            draw.text((140, top + 775), "Duong dan chi tiet nam ngay tai phan mo ta video!", font=f_sub, fill=(203, 213, 225))


    def _draw_cta(self, draw: ImageDraw.Draw, top: int, f_headline, f_node):
        self._draw_window_header(draw, top, "github_project_radar.channel")
        draw.rectangle([(100, top + 180), (980, top + 780)], fill=(24, 32, 47), outline=(37, 99, 235), width=4)
        draw.text((140, top + 250), "CẢM ƠN ANH EM ĐÃ XEM!", font=f_headline, fill=(241, 245, 249))
        draw.text((140, top + 340), "Đón xem các dự án mã nguồn mở bùng nổ tiếp theo", font=self._font(30), fill=(148, 163, 184))

        # CTA Action Button (strictly compliant with CTA policy)
        draw.rectangle([(140, top + 460), (940, top + 620)], fill=(37, 99, 235))
        draw.text((170, top + 510), "LIKE • SHARE • ĐĂNG KÝ KÊNH", font=self._font(44), fill=(255, 255, 255))
        draw.text((250, top + 690), "Hẹn gặp lại ở video tiếp theo!", font=f_node, fill=(52, 211, 153))

    def _draw_chapter_title_card(self, draw: ImageDraw.Draw, beat: VisualBeatEvent, top: int, f_headline, f_node, f_sub):
        self._draw_window_header(draw, top, "chapter_overview.index")
        draw.rectangle([(100, top + 140), (980, top + 740)], fill=(20, 29, 47), outline=(14, 165, 233), width=4)
        
        # Chapter Label & Number
        label_text = beat.sub_label or "CHAPTER"
        draw.rectangle([(140, top + 190), (460, top + 250)], fill=(14, 165, 233))
        draw.text((160, top + 204), label_text, font=self._font(28), fill=(10, 14, 23))

        # Chapter Title
        title_text = beat.headline_text or "CHAPTER OVERVIEW"
        draw.text((140, top + 290), title_text, font=self._font(42), fill=(255, 255, 255))

        # Retention hint / Subtitle
        if beat.diagram_elements and len(beat.diagram_elements) > 2 and beat.diagram_elements[2]:
            draw.text((140, top + 390), beat.diagram_elements[2], font=f_sub, fill=(148, 163, 184))
        else:
            draw.text((140, top + 390), "CONG NGHE // KIEN TRUC // PHAN TICH CHUYEN SAU", font=f_sub, fill=(148, 163, 184))

        draw.rectangle([(140, top + 520), (940, top + 570)], fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        draw.rectangle([(140, top + 520), (600, top + 570)], fill=(16, 185, 129))
        draw.text((150, top + 590), "CHUONG MUC CHINH • GITHUB PROJECT RADAR LONG-FORM", font=self._font(20), fill=(56, 189, 248))

    def generate_thumbnail(self, title: str, repo_name: str, thumbnail_text: str = "", output_path: Optional[str] = None) -> str:
        """Generates dedicated 16:9 1280x720 long-form YouTube thumbnail."""
        out_file = output_path or os.path.join(self.output_dir, f"thumb_{uuid.uuid4().hex[:8]}.png")
        t_width, t_height = 1280, 720
        img = Image.new("RGB", (t_width, t_height), color=(8, 12, 20))
        draw = ImageDraw.Draw(img)

        # Top border accent
        draw.rectangle([(0, 0), (t_width, 10)], fill=(14, 165, 233))

        # Badge
        draw.rectangle([(60, 50), (450, 100)], fill=(20, 30, 48), outline=(37, 99, 235), width=2)
        draw.text((80, 62), "GITHUB RADAR // DEEP DIVE", font=self._font(24), fill=(56, 189, 248))

        # High-contrast curiosity text (2-6 words)
        main_headline = (thumbnail_text or "AI THAY DOI MOI THU").upper()
        draw.rectangle([(50, 140), (1220, 320)], fill=(15, 23, 42), outline=(14, 165, 233), width=4)
        draw.text((80, 180), main_headline, font=self._font(64), fill=(255, 255, 255))

        # Repo box
        draw.rectangle([(60, 370), (700, 640)], fill=(24, 32, 47), outline=(59, 130, 246), width=3)
        draw.text((90, 400), f"REPOSITORY: {repo_name.upper()}", font=self._font(34), fill=(56, 189, 248))
        draw.text((90, 470), "MA NGUON MO • KIEN TRUC MOI", font=self._font(26), fill=(203, 213, 225))
        draw.rectangle([(90, 530), (400, 600)], fill=(234, 179, 8))
        draw.text((110, 545), "★ TRENDING #1", font=self._font(30), fill=(15, 23, 42))

        # Visual indicator block on right
        draw.rectangle([(750, 370), (1220, 640)], fill=(18, 25, 38), outline=(16, 185, 129), width=3)
        draw.text((780, 400), "TINH NANG DOT PHA:", font=self._font(26), fill=(52, 211, 153))
        draw.text((780, 460), "• Khong can setup phuc tap", font=self._font(24), fill=(226, 232, 240))
        draw.text((780, 510), "• Hieu qua cao hon 10 lan", font=self._font(24), fill=(226, 232, 240))
        draw.text((780, 560), "• Tuong thich moi model AI", font=self._font(24), fill=(226, 232, 240))

        img.save(out_file, "PNG")
        return out_file

    def generate_longform_assets(self, storyboard: Any) -> Any:
        """Generates assets for LongFormStoryboard."""
        rendered_paths = []
        for beat in storyboard.beats:
            path = self._render_beat_asset(beat, storyboard.repo_category)
            beat.asset_path = path
            rendered_paths.append(path)

        storyboard.rendered_assets = rendered_paths
        return storyboard

    def _draw_window_header(self, draw: ImageDraw.Draw, top: int, title: str):
        draw.ellipse([(90, top + 25), (112, top + 47)], fill=(239, 68, 68))
        draw.ellipse([(124, top + 25), (146, top + 47)], fill=(234, 179, 8))
        draw.ellipse([(158, top + 25), (180, top + 47)], fill=(34, 197, 94))
        draw.text((215, top + 24), title, font=self._font(22), fill=(148, 163, 184))
        draw.line([(60, top + 65), (1020, top + 65)], fill=(51, 65, 85), width=2)

    def _font(self, size: int):
        try:
            return ImageFont.truetype(self.font_path, size)
        except Exception:
            return ImageFont.load_default()
