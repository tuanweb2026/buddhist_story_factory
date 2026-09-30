import os
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
from radar.models.schemas import ScriptArtifact, VisualStoryboard, VisualScene


class VisualPlanningAgent:
    """Plans visual scenes mapped 1:1 to script segments with technical clarity in Vietnamese."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.shorts_cfg = config.get("formats", {}).get("shorts", {})
        self.width = self.shorts_cfg.get("width", 1080)
        self.height = self.shorts_cfg.get("height", 1920)

    def plan(self, script: ScriptArtifact) -> VisualStoryboard:
        scenes: List[VisualScene] = []
        
        headline_map = {
            "hook": "DỰ ÁN MÃ NGUỒN MỞ NỔI BẬT",
            "why_interesting": "ĐIỂM ĐẶC BIỆT",
            "core_explanation": "CÁI HAY Ở ĐÂY LÀ GÌ?",
            "why_care": "TẠI SAO ANH EM NÊN QUAN TÂM?",
            "cta_loop": "LIKE • SHARE • ĐĂNG KÝ KÊNH"
        }

        for seg in script.segments:
            headline = headline_map.get(seg.segment_type, seg.segment_type.upper())
            subtext = seg.spoken_text
            
            # For CTA screen, ensure exact policy compliance
            if seg.segment_type == "cta_loop":
                subtext = "LIKE • SHARE • ĐĂNG KÝ KÊNH"

            scene = VisualScene(
                order=seg.order,
                scene_id=f"{script.story_id}_scene_{seg.order}",
                visual_type=seg.visual_cue,
                title=script.title,
                headline=headline,
                subtext=subtext,
                badge_text="GITHUB RADAR // KHÁM PHÁ CÔNG NGHỆ",
                duration_sec=seg.estimated_duration_sec,
                is_synthetic=True,
                synthetic_notice="HÌNH ẢNH MINH HỌA KHÁI NIỆM • GITHUB PROJECT RADAR"
            )
            scenes.append(scene)

        total_dur = sum(s.duration_sec for s in scenes)
        return VisualStoryboard(
            story_id=script.story_id,
            scenes=scenes,
            total_duration_sec=total_dur
        )


class VisualAssetAgent:
    """Renders high-resolution typography, code cards, and UI mockups for 9:16 vertical video."""

    def __init__(self, config: Dict[str, Any], output_dir: str = "data/visuals"):
        self.config = config
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        shorts_cfg = config.get("formats", {}).get("shorts", {})
        self.width = shorts_cfg.get("width", 1080)
        self.height = shorts_cfg.get("height", 1920)
        self.font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if not os.path.exists(self.font_path):
            self.font_path = "/Library/Fonts/Arial Unicode.ttf"

    def generate_assets(self, storyboard: VisualStoryboard) -> VisualStoryboard:
        rendered_paths = []
        for scene in storyboard.scenes:
            path = self._render_scene_image(scene)
            scene.image_path = path
            rendered_paths.append(path)

        storyboard.rendered_assets = rendered_paths
        return storyboard

    def _render_scene_image(self, scene: VisualScene) -> str:
        out_path = os.path.join(self.output_dir, f"{scene.scene_id}.png")
        
        # Tech vertical aesthetic: 1080x1920 with high contrast
        img = Image.new("RGB", (self.width, self.height), color=(11, 15, 25))
        draw = ImageDraw.Draw(img)

        # Fonts
        font_badge = self._load_font(26)
        font_headline = self._load_font(46)
        font_content = self._load_font(38)
        font_small = self._load_font(24)

        # Top cyan-blue accent bar
        draw.rectangle([(0, 0), (self.width, 20)], fill=(14, 165, 233))

        # Top Badge Box
        badge_y = 130
        draw.rectangle([(80, badge_y), (1000, badge_y + 70)], fill=(30, 41, 59))
        draw.text((100, badge_y + 18), scene.badge_text, font=font_badge, fill=(148, 163, 184))

        # Scene Headline (60-80px padding for mobile safe zone)
        headline_y = 250
        draw.text((80, headline_y), scene.headline, font=font_headline, fill=(56, 189, 248))

        # Central Visual Content Card (Terminal / Code / Metric Box)
        card_top = 370
        card_bottom = 1450
        draw.rectangle([(70, card_top), (1010, card_bottom)], fill=(17, 24, 39), outline=(51, 65, 85), width=4)

        # Terminal style controls (3 dots)
        draw.ellipse([(100, card_top + 30), (122, card_top + 52)], fill=(239, 68, 68))
        draw.ellipse([(137, card_top + 30), (159, card_top + 52)], fill=(234, 179, 8))
        draw.ellipse([(174, card_top + 30), (196, card_top + 52)], fill=(34, 197, 94))
        draw.text((230, card_top + 28), f"mode: {scene.visual_type}", font=font_small, fill=(148, 163, 184))

        # Card Content Text
        if scene.subtext == "LIKE • SHARE • ĐĂNG KÝ KÊNH":
            # Distinctive CTA layout
            cta_font = self._load_font(52)
            draw.text((120, card_top + 300), "CẢM ƠN ANH EM ĐÃ XEM!", font=font_headline, fill=(241, 245, 249))
            draw.rectangle([(110, card_top + 450), (970, card_top + 600)], fill=(37, 99, 235))
            draw.text((140, card_top + 500), "LIKE • SHARE • ĐĂNG KÝ KÊNH", font=cta_font, fill=(255, 255, 255))
        else:
            content_lines = self._wrap_text(scene.subtext, max_chars=34)
            curr_y = card_top + 130
            for line in content_lines[:12]:
                draw.text((110, curr_y), line, font=font_content, fill=(241, 245, 249))
                curr_y += 68

        # Footer Synthetic Notice (Ensuring transparency)
        if scene.is_synthetic and scene.synthetic_notice:
            draw.text((80, 1780), scene.synthetic_notice, font=font_small, fill=(100, 116, 139))

        # Channel Watermark
        draw.text((80, 1825), "GITHUB PROJECT RADAR V2 • AUTONOMOUS RADAR", font=font_small, fill=(71, 85, 105))

        img.save(out_path, "PNG")
        return out_path

    def _load_font(self, size: int):
        try:
            return ImageFont.truetype(self.font_path, size)
        except Exception:
            return ImageFont.load_default()

    def _wrap_text(self, text: str, max_chars: int = 34) -> List[str]:
        words = text.split()
        lines = []
        curr = []
        curr_len = 0
        for w in words:
            if curr_len + len(w) + 1 > max_chars:
                lines.append(" ".join(curr))
                curr = [w]
                curr_len = len(w)
            else:
                curr.append(w)
                curr_len += len(w) + 1
        if curr:
            lines.append(" ".join(curr))
        return lines
