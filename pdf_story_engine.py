#!/usr/bin/env python3
"""
Buddhist Story Factory: PDF to Buddhist Art Video Engine
1. Reads Buddhist text from PDF
2. Generates serene, sacred Buddhist art illustrations
3. Dubs narration with Vietnamese Microsoft Neural Voice (vi-VN-HoaiMyNeural)
4. Renders complete synchronized video (with slow camera push-in motion) using FFmpeg
"""

import os
import re
import sys
import time
import asyncio
import subprocess
import argparse
import urllib.parse
import urllib.request
import pypdf
import edge_tts
from PIL import Image
import io


BUDDHIST_STYLE_TAGS = (
    "traditional Buddhist fine art, sacred and serene atmosphere, soft golden divine aura, "
    "ancient monastery garden, lotus flowers, peaceful zen composition, masterwork oil painting, "
    "sacred lighting, elegant brushwork, highly detailed 8k, sharp focus, "
    "no modern technology, no cars, no modern clothes, no distorted anatomy, no cartoon"
)


def extract_text_from_pdf(pdf_path: str, max_pages: int = 50) -> str:
    """Extracts text from a given PDF or text file."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Tệp không tồn tại: {pdf_path}")

    # Support plain text or markdown directly
    if pdf_path.endswith((".txt", ".md")):
        with open(pdf_path, "r", encoding="utf-8") as f:
            return f.read()

    # If a clean script .txt exists alongside the PDF, prefer it
    txt_sidecar = os.path.splitext(pdf_path)[0] + ".txt"
    if os.path.exists(txt_sidecar):
        print(f"[*] Tìm thấy kịch bản văn bản chuẩn đi kèm tại: {txt_sidecar}")
        with open(txt_sidecar, "r", encoding="utf-8") as f:
            return f.read()

    reader = pypdf.PdfReader(pdf_path)
    full_paragraphs = []
    total_pages = min(len(reader.pages), max_pages)

    print(f"[*] Đang đọc tệp PDF: {pdf_path} ({total_pages} trang)...")
    for i in range(total_pages):
        page_text = reader.pages[i].extract_text() or ""
        # Group lines preserving paragraphs
        lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in page_text.splitlines()]
        current_para = []
        for line in lines:
            if not line:
                if current_para:
                    full_paragraphs.append(" ".join(current_para))
                    current_para = []
            else:
                current_para.append(line)
        if current_para:
            full_paragraphs.append(" ".join(current_para))

    extracted = "\n\n".join(full_paragraphs).strip()
    # Fallback to Apple Vision native OCR if PDF has outlined/scanned text
    if len(extracted) < 50:
        print("[*] Tệp PDF dạng tranh/outline vector, đang kích hoạt Apple Vision OCR siêu nhanh...")
        ocr_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "macos_pdf_ocr")
        if os.path.exists(ocr_bin):
            res = subprocess.run([ocr_bin, os.path.abspath(pdf_path)], stdout=subprocess.PIPE, text=True)
            if res.returncode == 0 and len(res.stdout.strip()) > 30:
                extracted = res.stdout.strip()
                print(f"[+] OCR thành công: Trích xuất được {len(extracted)} ký tự từ file PDF!")

    return extracted


def segment_text_into_scenes(text: str, max_scenes: int = 15) -> list:
    """Splits Buddhist story text into cohesive narrative scenes/beats."""
    # Split by double newline or chapter/section markers
    raw_blocks = [b.strip() for b in re.split(r'\n\s*\n|(?=Đoạn\s+\d+:|Doan\s+\d+:|Chương\s+\d+:)', text) if b.strip()]
    
    refined_scenes = []
    for block in raw_blocks:
        # Ignore titles, uppercase book headers, or tiny blocks
        if len(block) < 20 or block.isupper() or (len(block) < 45 and not block.endswith((".", "!", "?"))):
            continue
        
        # If block is too long (> 350 chars), break by sentences
        if len(block) > 350:
            sentences = re.split(r'(?<=[.!?])\s+', block)
            curr = ""
            for s in sentences:
                if len(curr) + len(s) < 300:
                    curr = (curr + " " + s).strip()
                else:
                    if curr:
                        refined_scenes.append(curr)
                    curr = s
            if curr:
                refined_scenes.append(curr)
        else:
            refined_scenes.append(block)

    scenes = []
    for i, s_text in enumerate(refined_scenes[:max_scenes]):
        scenes.append({
            "scene_id": f"scene_{i+1:02d}",
            "order": i + 1,
            "text": s_text
        })

    return scenes


def build_buddhist_image_prompt(scene_text: str, scene_order: int = 1) -> str:
    """Intelligently detects the precise action, actors, setting, and mood of each scene."""
    t_lower = scene_text.lower()
    
    # 1. Đặt bát cơm dỗ dành rắn ăn
    if any(k in t_lower for k in ["kiếm chút cơm", "rắn ơi", "đem cơm", "bát cơm", "ăn cơm nhé", "chút cơm", "cơm bánh"]):
        subject = (
            "A benevolent Buddhist monk in saffron robes kneeling gently by lush wild garden bushes at sunset, "
            "placing a small handcrafted ceramic bowl of white cooked rice on the mossy green grass, "
            "gesturing kindly with an open hand, a slender harmless garden snake peeking out safely from behind leaves, "
            "warm golden sunset radiance, touching scene of pure compassion and peace"
        )
    # 2. Triết lý Nhân quả, Từ bi & Bình đẳng muôn loài
    elif any(k in t_lower for k in ["nhân quả", "đạo đức từ bi", "không nỡ để một", "quy luật tự nhiên"]):
        subject = (
            "A serene panoramic wide view of an ancient Asian Buddhist pagoda courtyard at twilight, "
            "gentle incense smoke curling from a bronze burner, blooming sacred pink lotus pond in foreground, "
            "soft glowing stone lantern, peaceful starry twilight sky, spiritual harmony, universal peace and karma"
        )
    # 3. Khoảnh khắc can thiệp cứu nhái khỏi rắn
    elif any(k in t_lower for k in ["cứu nhái", "đi nhanh ra cứu", "rắn sẽ bị đói", "để rắn giết nhái", "rắn lại mang thêm tội"]):
        subject = (
            "A compassionate Buddhist monk in saffron robes standing in tall green grass by a garden slope, "
            "gently bending down with open hands to rescue a tiny green tree frog from a surprised garden snake, "
            "peaceful protective gesture without harm, wild ferns and moss, warm golden light, sacred empathy"
        )
    # 4. Nghe tiếng kêu cứu thất thanh bên ngoài cửa sổ
    elif any(k in t_lower for k in ["nghe tiếng kêu cứu", "nghe tiếng nhái", "bị rắn cắn", "tiếng kêu cứu", "bỗng nhiên thầy nghe"]):
        subject = (
            "A startled Buddhist monk pausing his work at a rustic wooden study desk, turning his head towards an open wooden window, "
            "looking outside into the misty green monastery garden in alarm, dramatic spiritual storytelling composition, "
            "rays of dawn light, empathy and tension"
        )
    # 5. Thầy ngồi viết sách, chấm bài trong thư phòng tu viện
    elif any(k in t_lower for k in ["chấm bài", "viết sách", "tu sinh", "chánh kiến", "ngồi say sưa làm việc", "thư phòng"]):
        subject = (
            "Inside a quiet traditional monastery study room, an elderly Vietnamese Buddhist monk in saffron robes "
            "sitting at an antique wooden writing desk, holding a traditional bamboo calligraphy ink brush, "
            "neat stacks of manuscripts and student exam papers, soft morning sunlight streaming through paper lattice windows, "
            "contemplative serenity, scholarly zen environment"
        )
    # 6. Khu hầm cỏ rậm rạp, hệ sinh thái tự nhiên
    elif any(k in t_lower for k in ["cái hầm", "cỏ mọc um tùm", "rậm rạp", "trú ẩn", "thức ăn của loài khác"]):
        subject = (
            "An overgrown wild corner of an ancient Buddhist monastery garden, a natural earthen hollow burrow nestled beneath twisted mossy tree roots, "
            "tall wild blades of green grass, tiny insects, dewdrops, misty deep green nature habitat, "
            "filtered sunbeams, peaceful primeval sanctuary, no modern objects"
        )
    # 7. Đức Phật thiền định dưới cội Bồ Đề
    elif any(k in t_lower for k in ["bồ đề", "giác ngộ", "thành đạo", "ngồi thiền", "thiền định", "bodh gaya"]):
        subject = (
            "The Buddha meditating peacefully under the ancient sacred Bodhi tree at sunrise, serene facial expression, "
            "divine warm golden halo behind head, gentle golden light rays filtering through leaves"
        )
    # 8. Chư Tăng khất thực
    elif any(k in t_lower for k in ["khất thực", "chư tăng", "đoàn tăng", "tăng đoàn", "áo cà sa", "y cà sa", "bình bát"]):
        subject = (
            "A tranquil procession of Buddhist monks walking barefoot in traditional saffron robes through an ancient quiet misty village at dawn, "
            "holding alms bowls, peaceful and mindful steps"
        )
    # 9. Bồ Tát Quán Thế Âm
    elif any(k in t_lower for k in ["bồ tát", "quán thế âm", "quan âm", "cứu khổ"]):
        subject = (
            "Avalokiteshvara Bodhisattva of compassion standing gracefully on a pure white lotus pedestal over ocean waves, "
            "holding willow branch and nectar vase, divine soft white and gold aura"
        )
    else:
        subject = (
            f"Scene {scene_order}: Peaceful ancient Buddhist narrative scene, gentle morning light, sacred atmosphere, "
            "tranquil monk in traditional robes, peaceful monastery garden with ancient trees and soft incense mist"
        )

    return f"{subject}, {BUDDHIST_STYLE_TAGS}"


def download_buddhist_image(
    prompt: str,
    out_path: str,
    width: int = 1080,
    height: int = 1920,
    retries: int = 3,
    seed: int = None,
    force: bool = False
) -> bool:
    """Fetches high-quality artwork from Pollinations FLUX / Turbo API with retries, unique seed, and fallbacks."""
    if not force and os.path.exists(out_path) and os.path.getsize(out_path) > 2000:
        return True

    # Truncate prompt if extremely long to avoid URL limits
    clean_prompt = prompt.strip()
    if len(clean_prompt) > 300:
        clean_prompt = clean_prompt[:297] + "..."

    encoded = urllib.parse.quote(clean_prompt)
    req_w = 768 if width < height else 1024
    req_h = 1024 if width < height else 768
    
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    
    # Try flux, turbo, and pollinations default with unique seed
    models = ["flux", "turbo", ""]
    seed_val = seed if seed is not None else abs(hash(prompt)) % 999999
    
    for attempt in range(retries):
        model_param = f"&model={models[attempt % len(models)]}" if models[attempt % len(models)] else ""
        url = f"https://image.pollinations.ai/prompt/{encoded}?width={req_w}&height={req_h}&nologo=true&seed={seed_val}{model_param}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = resp.read()
                if len(data) < 1000:
                    continue
                img = Image.open(io.BytesIO(data)).convert("RGB")
                if img.height > 100:
                    img = img.crop((0, 0, img.width, img.height - 35))
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
                img.save(out_path, "PNG")
                return True
        except Exception as e:
            time.sleep(2.0)
    return False


async def synthesize_voice_async(text: str, out_path: str, voice: str = "vi-VN-HoaiMyNeural", retries: int = 3) -> bool:
    """Synthesize Vietnamese audio using Microsoft Neural Voice via edge-tts."""
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        return True

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    clean_text = text.replace(" ... ", ". ").replace("...", ".").strip()
    if not clean_text.endswith((".", "!", "?")):
        clean_text += "."

    for attempt in range(retries):
        try:
            comm = edge_tts.Communicate(clean_text, voice, rate="-4%")
            await comm.save(out_path)
            if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
                return True
        except Exception as e:
            if attempt == retries - 1:
                # Fallback to secondary voice if primary fails
                fallback_voice = "vi-VN-NamMinhNeural" if voice == "vi-VN-HoaiMyNeural" else "vi-VN-HoaiMyNeural"
                try:
                    comm = edge_tts.Communicate(clean_text, fallback_voice, rate="-4%")
                    await comm.save(out_path)
                    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
                        return True
                except Exception:
                    pass
                print(f"    [!] Lỗi lồng tiếng ({voice}): {e}")
            await asyncio.sleep(2.0)
    return False


def synthesize_voice(text: str, out_path: str, voice: str = "vi-VN-HoaiMyNeural") -> bool:
    return asyncio.run(synthesize_voice_async(text, out_path, voice))


def get_audio_duration(audio_path: str) -> float:
    """Gets audio duration in seconds using ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", audio_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        return 5.0


def apply_subtitles_to_image(image_path: str, text: str, out_path: str, width: int = 1080, height: int = 1920) -> str:
    """Renders elegant, sacred subtitle text at the bottom with a subtle darkened translucent banner."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.open(image_path).convert("RGBA")
        
        # Create an overlay for subtle gradient/dark box at bottom for readability
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        
        banner_h = int(height * 0.16) if height > width else int(height * 0.20)
        banner_y = height - banner_h - int(height * 0.05)
        
        # Semi-transparent dark pill background
        margin_x = int(width * 0.05)
        draw_ov.rounded_rectangle(
            [(margin_x, banner_y), (width - margin_x, height - int(height * 0.05))],
            radius=24,
            fill=(12, 16, 24, 185)
        )
        img = Image.alpha_composite(img, overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        # Font setup
        font_size = int(width * 0.035)
        font = None
        for font_path in [
            "/Library/Fonts/Arial Unicode.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except Exception:
                    continue
        if font is None:
            font = ImageFont.load_default()
            
        # Wrap text into lines
        words = text.split()
        lines = []
        cur_line = ""
        max_chars = 34 if width < height else 55
        for w in words:
            if len(cur_line) + len(w) + 1 <= max_chars:
                cur_line = (cur_line + " " + w).strip()
            else:
                if cur_line:
                    lines.append(cur_line)
                cur_line = w
        if cur_line:
            lines.append(cur_line)
            
        # Draw wrapped lines centered
        line_spacing = int(font_size * 1.38)
        total_text_h = len(lines) * line_spacing
        start_y = banner_y + max(10, (banner_h - total_text_h) // 2)
        
        for idx, line in enumerate(lines[:3]):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_w = bbox[2] - bbox[0]
            x = (width - text_w) // 2
            y = start_y + idx * line_spacing
            draw.text((x, y), line, font=font, fill=(255, 248, 225))
            
        img.save(out_path, "PNG")
        return out_path
    except Exception as e:
        print(f"    [!] Lỗi phủ phụ đề: {e}")
        return image_path


def render_scene_clip(image_path: str, audio_path: str, out_clip_path: str, width: int = 1080, height: int = 1920, fps: int = 30) -> bool:
    """Renders a single scene clip matching the audio length with subtle zoom motion."""
    dur = get_audio_duration(audio_path)
    # Add 0.5s pause at end of each scene for smooth listening
    dur += 0.5
    num_frames = int(dur * fps)

    # Subtle smooth push-in zoompan
    zoom_filter = f"zoompan=z='min(zoom+0.0003,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={num_frames}:s={width}x{height}:fps={fps}"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", os.path.abspath(image_path),
        "-i", os.path.abspath(audio_path),
        "-vf", f"{zoom_filter},format=yuv420p",
        "-t", f"{dur:.2f}",
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        out_clip_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.returncode == 0 and os.path.exists(out_clip_path)


def concatenate_clips(clip_paths: list, output_video: str) -> bool:
    """Concatenates all scene clips into a single video."""
    os.makedirs(os.path.dirname(os.path.abspath(output_video)), exist_ok=True)
    list_file = output_video.replace(".mp4", "_clips.txt")

    with open(list_file, "w", encoding="utf-8") as f:
        for p in clip_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        output_video
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if os.path.exists(list_file):
        os.remove(list_file)
    return res.returncode == 0 and os.path.exists(output_video)


def process_pdf_to_video(
    pdf_path: str,
    output_dir: str = "data/buddhist_production",
    orientation: str = "portrait",
    voice: str = "vi-VN-HoaiMyNeural",
    with_subtitles: bool = True,
    max_scenes: int = 10,
    force: bool = False
):
    """Full End-to-End Pipeline: PDF -> Storyboard -> Illustrations -> Hoai My Voice -> Rendered Video."""
    import json
    story_slug = os.path.splitext(os.path.basename(pdf_path))[0]
    prod_dir = os.path.join(output_dir, story_slug)
    visuals_dir = os.path.join(prod_dir, "visuals")
    audio_dir = os.path.join(prod_dir, "audio")
    clips_dir = os.path.join(prod_dir, "clips")
    os.makedirs(visuals_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(clips_dir, exist_ok=True)

    w, h = (1080, 1920) if orientation == "portrait" else (1920, 1080)
    final_video_path = os.path.join(prod_dir, f"{story_slug}_{orientation}.mp4")

    # 1. Extract Text
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("[!] Không tìm thấy văn bản trong file PDF.")
        return

    # 2. Segment Scenes
    scenes = segment_text_into_scenes(text, max_scenes=max_scenes)
    print(f"\n[+] Đã chia kịch bản thành {len(scenes)} phân cảnh Phật giáo.")

    rendered_clips = []
    storyboard = []

    # 3. Process Each Scene
    for s in scenes:
        scene_id = s["scene_id"]
        scene_text = s["text"]
        order = s["order"]
        print(f"\n=======================================================")
        print(f"[*] ĐANG XỬ LÝ CẢNH {order}/{len(scenes)}: {scene_id.upper()}")
        print(f"    Lời dẫn: \"{scene_text}\"")

        # A. Image generation with exact scene action prompt and unique seed
        raw_img_path = os.path.join(visuals_dir, f"{scene_id}_raw.png")
        prompt = build_buddhist_image_prompt(scene_text, scene_order=order)
        seed = (order * 8461 + 19283) % 999999
        print(f"    [1/3] Đang tạo tranh minh họa bám sát hành động (Seed: {seed})...")
        print(f"    [Prompt]: {prompt[:120]}...")
        img_ok = download_buddhist_image(prompt, raw_img_path, width=w, height=h, seed=seed, force=force)
        if not img_ok:
            print(f"    [!] Lỗi tạo ảnh cho cảnh {scene_id}")
            continue

        # Subtitle overlay
        active_img_path = os.path.join(visuals_dir, f"{scene_id}.png")
        if with_subtitles:
            apply_subtitles_to_image(raw_img_path, scene_text, active_img_path, width=w, height=h)
        else:
            active_img_path = raw_img_path

        # B. Vietnamese Voiceover (Hoai My)
        audio_path = os.path.join(audio_dir, f"{scene_id}.mp3")
        print(f"    [2/3] Đang lồng tiếng giọng Hoài My (vi-VN-HoaiMyNeural)...")
        voice_ok = synthesize_voice(scene_text, audio_path, voice=voice)
        if not voice_ok:
            print(f"    [!] Lỗi lồng tiếng cho cảnh {scene_id}")
            continue

        # C. Render Scene Video Clip
        clip_path = os.path.join(clips_dir, f"{scene_id}.mp4")
        print(f"    [3/3] Đang render clip phân cảnh (chuyển động camera thanh tịnh)...")
        clip_ok = render_scene_clip(active_img_path, audio_path, clip_path, width=w, height=h)
        if clip_ok:
            rendered_clips.append(clip_path)
            print(f"    [OK] Hoàn tất phân cảnh {scene_id}!")

        storyboard.append({
            "scene_id": scene_id,
            "order": order,
            "text": scene_text,
            "prompt": prompt,
            "seed": seed,
            "visual_raw": raw_img_path,
            "visual_subtitled": active_img_path,
            "audio": audio_path,
            "clip": clip_path
        })

    # Save Storyboard JSON for audit and transparency
    storyboard_path = os.path.join(prod_dir, "storyboard.json")
    with open(storyboard_path, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, ensure_ascii=False, indent=2)
    print(f"\n[+] Đã lưu Storyboard chi tiết tại: {storyboard_path}")

    # 4. Concatenate All Clips
    if rendered_clips:
        print(f"\n[*] ĐANG GHÉP TOÀN BỘ {len(rendered_clips)} PHÂN CẢNH THÀNH VIDEO HOÀN CHỈNH...")
        success = concatenate_clips(rendered_clips, final_video_path)
        if success:
            dur = get_audio_duration(final_video_path)
            size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
            print(f"\n🎉 XUẤT SẮC! VIDEO TRUYỆN PHẬT GIÁO ĐÃ HOÀN TẤT:")
            print(f"    - Đường dẫn video: {final_video_path}")
            print(f"    - Thời lượng: {dur:.2f}s ({w}x{h})")
            print(f"    - Dung lượng: {size_mb:.2f} MB")
            print(f"    - Giọng đọc: {voice} (Microsoft Neural Voice)")
    else:
        print("[!] Không có phân cảnh nào được render thành công.")


def main():
    parser = argparse.ArgumentParser(description="Buddhist Story Factory: PDF to Buddhist Art Video Engine")
    parser.add_argument("--pdf", required=True, help="Đường dẫn tới file PDF hoặc file văn bản truyện Phật giáo")
    parser.add_argument("--output", default="data/buddhist_production", help="Thư mục xuất video")
    parser.add_argument("--orientation", default="portrait", choices=["portrait", "landscape"], help="portrait (9:16 Shorts/TikTok) hoặc landscape (16:9 YouTube)")
    parser.add_argument("--voice", default="vi-VN-HoaiMyNeural", help="Giọng đọc tiếng Việt (mặc định: vi-VN-HoaiMyNeural)")
    parser.add_argument("--no-subtitles", action="store_true", help="Không chèn phụ đề chữ lên tranh")
    parser.add_argument("--max-scenes", type=int, default=10, help="Số phân cảnh tối đa tạo ra")
    parser.add_argument("--force", action="store_true", help="Buộc tạo lại toàn bộ tranh và video mới")
    args = parser.parse_args()

    process_pdf_to_video(
        args.pdf,
        args.output,
        args.orientation,
        args.voice,
        with_subtitles=not args.no_subtitles,
        max_scenes=args.max_scenes,
        force=args.force
    )


if __name__ == "__main__":
    main()
