import os
import io
import time
import urllib.parse
import urllib.request
from typing import Optional
from PIL import Image

try:
    from radar.models.schemas import VisualBeatEvent
except ImportError:
    VisualBeatEvent = None


def build_beat_prompt(beat, repo_category: str = "DEV_TOOL", repo_name: str = "") -> str:
    """Constructs an accurate, high-fidelity English visual prompt from a VisualBeatEvent."""
    v_type = getattr(beat, "visual_type", "").upper()
    headline = getattr(beat, "headline_text", "")
    sub_label = getattr(beat, "sub_label", "")
    action = getattr(beat, "visual_action", "")
    target = getattr(beat, "attention_target", "")
    
    # Base concept mapping
    if v_type in ["REAL_REPOSITORY_UI", "REPOSITORY_HOOK", "STAR_COUNT_HOOK"]:
        concept = f"holographic GitHub repository dashboard displaying trending metrics, high-tech glowing star counter and code stats for open-source project {repo_name}"
    elif v_type in ["TECHNICAL_FLOW", "AGENT_WORKFLOW"]:
        concept = "3D isometric flowchart visualization of autonomous AI agent workflow, neural data pipeline, glowing connectors and nodes, cybernetic data stream"
    elif v_type in ["BROWSER_DEMO", "BROWSER_INTERACTION", "DEVICE_INTERACTION"]:
        concept = "futuristic interactive web browser interface operated by autonomous AI agent, glowing HUD elements, holographic cursor clicking web elements"
    elif v_type in ["TERMINAL_DEMO", "CODE_VISUALIZATION"]:
        concept = "sleek ultra-futuristic developer terminal ide screen displaying code compilation, glowing syntax, dark slate matrix background"
    elif v_type in ["ARCHITECTURE_DIAGRAM", "SYSTEM_DIAGRAM", "HARDWARE_VISUALIZATION"]:
        concept = "isometric 3D blueprint system architecture diagram, microservices, neural network layers, hardware chips and glowing data buses"
    elif v_type == "BEFORE_AFTER":
        concept = "futuristic split comparison, obsolete legacy code on left vs blazing fast modern AI engine on right, neon lighting"
    elif v_type == "DATA_VISUALIZATION":
        concept = "futuristic holographic benchmark data visualization, 3D performance graphs, latency metrics and throughput charts glowing"
    elif v_type in ["PAYOFF_VISUAL", "RESULT_PAYOFF"]:
        concept = "futuristic tech achievement glowing trophy interface, successful AI execution summary, sleek cyberpunk dashboard"
    elif v_type == "CTA":
        concept = "modern tech channel subscribe outro screen, neon glowing buttons, futuristic developer aesthetic"
    elif v_type == "CHAPTER_TITLE_CARD":
        concept = f"cinematic sci-fi chapter title screen, glowing neon typography '{headline}', deep dark space tech background"
    else:
        concept = f"high-tech concept illustration for {headline or 'software engineering'}, glowing data streams"

    # Add specifics
    extras = []
    if target:
        extras.append(f"focusing on {target}")
    if action:
        extras.append(f"showing {action}")

    specifics = ", ".join(extras)
    if specifics:
        prompt = f"{concept}, {specifics}"
    else:
        prompt = concept

    # Standard styling for visual consistency (Strict IT / Software Engineering Only)
    style = "strictly modern software engineering and IT tech context, clean code interface and server architecture, dark slate palette, glowing cyan accents, 8k octane render, photorealistic 3D tech illustration, sharp focus, no humans, no faces, no aliens, no robots, no monsters, no groceries, no food"
    return f"{prompt}, {style}"


def fetch_ai_image(
    prompt: str,
    width: int = 960,
    height: int = 1180,
    cache_path: Optional[str] = None,
    timeout: int = 25,
    retries: int = 2
) -> Optional[Image.Image]:
    """Downloads an AI generated illustration from Pollinations free text-to-image API.
    
    Returns PIL Image resized to (width, height), or None if unavailable.
    """
    if cache_path and os.path.exists(cache_path) and os.path.getsize(cache_path) > 1000:
        try:
            return Image.open(cache_path).convert("RGB")
        except Exception:
            pass

    encoded = urllib.parse.quote(prompt.strip())
    # Request proportional resolution for speed and stability
    req_w = min(width, 1024)
    req_h = min(height, 1024)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={req_w}&height={req_h}&nologo=true"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
    }

    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
                if len(data) < 500:
                    time.sleep(1.0)
                    continue
                img = Image.open(io.BytesIO(data)).convert("RGB")
                # Crop bottom 40px to ensure zero watermark
                if img.height > 100:
                    img = img.crop((0, 0, img.width, img.height - 35))
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                if cache_path:
                    os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
                    img.save(cache_path, "PNG")
                return img
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
            else:
                print(f"[!] AI image generator fallback triggered ({e})")
                return None

    return None
