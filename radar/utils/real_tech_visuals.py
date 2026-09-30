import os
import io
import re
import time
import urllib.parse
import urllib.request
from typing import Optional, List, Dict
from PIL import Image

# Curated, 100% verified real IT, software engineering, and hardware photography
TECH_STOCK_LIBRARY: Dict[str, List[str]] = {
    "REPOSITORY_UI": [
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085",  # MacBook code
        "https://images.unsplash.com/photo-1555066931-4365d14bab8c"   # Terminal code
    ],
    "DATA_CENTER": [
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31",  # Server racks, blue fiber cables
        "https://images.unsplash.com/photo-1544197150-b99a580bb7a8"   # High-density enterprise server
    ],
    "DEVELOPER_WORKSPACE": [
        "https://images.unsplash.com/photo-1498050108023-c5249f4df085",  # Clean developer laptop setup
        "https://images.unsplash.com/photo-1522071820081-009f0129c71c"   # Software engineers collaborating
    ],
    "HARDWARE_CHIP": [
        "https://images.unsplash.com/photo-1518770660439-4636190af475",  # Silicon motherboard chip
        "https://images.unsplash.com/photo-1591488320449-011701bb6704"   # High-tech circuit board
    ],
    "AI_NETWORK": [
        "https://images.unsplash.com/photo-1620712943543-bcc4688e7485",  # AI data visualization
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa"   # Global tech network
    ],
    "TECH_PAYOFF": [
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c",  # Modern tech workspace payoff
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa"   # Global cloud network
    ]
}


def fetch_image_from_url(url: str, width: int = 960, height: int = 1180, cache_path: Optional[str] = None, timeout: int = 15) -> Optional[Image.Image]:
    """Downloads an image from URL, crops to aspect ratio, resizes to (width, height), and caches locally."""
    if cache_path and os.path.exists(cache_path) and os.path.getsize(cache_path) > 1000:
        try:
            return Image.open(cache_path).convert("RGB")
        except Exception:
            pass

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            if len(data) < 500:
                return None
            img = Image.open(io.BytesIO(data)).convert("RGB")
            
            target_ratio = width / height
            img_ratio = img.width / img.height
            if img_ratio > target_ratio:
                new_w = int(img.height * target_ratio)
                left = (img.width - new_w) // 2
                img = img.crop((left, 0, left + new_w, img.height))
            else:
                new_h = int(img.width / target_ratio)
                top = (img.height - new_h) // 2
                img = img.crop((0, top, img.width, top + new_h))

            img = img.resize((width, height), Image.Resampling.LANCZOS)
            if cache_path:
                os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
                img.save(cache_path, "PNG")
            return img
    except Exception:
        return None


def get_github_repo_card(owner: str, repo_name: str, width: int = 960, height: int = 1180, cache_dir: str = "data/visuals/real_tech_cache") -> Optional[Image.Image]:
    """Fetches the official GitHub OpenGraph preview card for the repository."""
    cache_file = os.path.join(cache_dir, f"{owner}_{repo_name}_card.png")
    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 1000:
        try:
            return Image.open(cache_file).convert("RGB")
        except Exception:
            pass

    card_url = f"https://opengraph.githubassets.com/1/{owner}/{repo_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        req = urllib.request.Request(card_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            card_img = Image.open(io.BytesIO(data)).convert("RGB")
            
            canvas = Image.new("RGB", (width, height), color=(15, 23, 42))
            scaled_w = width - 40
            scaled_h = int(card_img.height * (scaled_w / card_img.width))
            card_img = card_img.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
            
            paste_y = (height - scaled_h) // 2
            canvas.paste(card_img, (20, paste_y))
            
            os.makedirs(cache_dir, exist_ok=True)
            canvas.save(cache_file, "PNG")
            return canvas
    except Exception:
        return None


def get_github_readme_images(owner: str, repo_name: str, timeout: int = 10) -> List[str]:
    """Scrapes actual demo images / architecture diagrams from the repository README.md."""
    branches = ["main", "master"]
    found_urls = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for branch in branches:
        readme_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/README.md"
        try:
            req = urllib.request.Request(readme_url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
                imgs = re.findall(r'!\[.*?\]\((https?://[^\)]+\.(?:png|jpg|jpeg|gif|webp))\)', content)
                imgs += re.findall(r'<img[^>]+src=[\"\'](https?://[^\'\"]+\.(?:png|jpg|jpeg|gif|webp))[\"\']', content)
                for u in imgs:
                    lower_u = u.lower()
                    if any(badge in lower_u for badge in ["badge", "shields.io", "fury.io", "codecov", "pepy.tech", "sonar", "travis"]):
                        continue
                    found_urls.append(u)
                if found_urls:
                    break
        except Exception:
            continue
    return found_urls


def get_real_tech_visual(beat, repo_full_name: str = "", width: int = 960, height: int = 1180, cache_dir: str = "data/visuals/real_tech_cache") -> Optional[Image.Image]:
    """Smart dispatcher that selects 100% REAL tech/IT imagery matching the beat context.
    
    IMPORTANT: Terminal demos and interactive code are handled natively by PIL drawing 
    to show the EXACT Python code lines, rather than generic stock photos.
    """
    v_type = getattr(beat, "visual_type", "").upper()

    # Never override technical flows, terminal demos, browser demos, comparisons, benchmarks, or payoffs
    # with generic stock photos. Keep 100% precise technical drawings!
    if v_type not in ["REAL_REPOSITORY_UI", "REPOSITORY_HOOK"]:
        return None

    os.makedirs(cache_dir, exist_ok=True)
    beat_id = getattr(beat, "beat_id", "beat")
    cache_path = os.path.join(cache_dir, f"{beat_id}_real.png")

    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 1000:
        try:
            return Image.open(cache_path).convert("RGB")
        except Exception:
            pass

    owner, repo_name = "browser-use", "browser-use"
    if "/" in repo_full_name:
        parts = repo_full_name.split("/")
        owner, repo_name = parts[0], parts[1]

    # 1. First priority for Hook / Repo UI / Star count: Official GitHub Repo Card
    if v_type in ["REAL_REPOSITORY_UI", "REPOSITORY_HOOK", "STAR_COUNT_HOOK"] or "B01" in beat_id or "B02" in beat_id:
        card = get_github_repo_card(owner, repo_name, width=width, height=height, cache_dir=cache_dir)
        if card:
            return card

    # 2. Check for real README demo screenshots
    readme_imgs = get_github_readme_images(owner, repo_name)
    if readme_imgs and v_type in ["TECHNICAL_FLOW", "AGENT_WORKFLOW"]:
        img = fetch_image_from_url(readme_imgs[0], width=width, height=height, cache_path=cache_path)
        if img:
            return img

    # 3. Choose from real IT stock photography library
    if v_type in ["ARCHITECTURE_DIAGRAM", "SYSTEM_DIAGRAM", "DATA_CENTER"]:
        pool = TECH_STOCK_LIBRARY["DATA_CENTER"]
    elif v_type in ["HARDWARE_VISUALIZATION"]:
        pool = TECH_STOCK_LIBRARY["HARDWARE_CHIP"]
    elif v_type in ["PAYOFF_VISUAL", "RESULT_PAYOFF"]:
        pool = TECH_STOCK_LIBRARY["TECH_PAYOFF"]
    elif v_type in ["BEFORE_AFTER", "WHY_CARE"]:
        pool = TECH_STOCK_LIBRARY["DEVELOPER_WORKSPACE"]
    else:
        pool = TECH_STOCK_LIBRARY["AI_NETWORK"]

    idx = abs(hash(beat_id)) % len(pool)
    stock_url = pool[idx] + f"?w={width}&h={height}&fit=crop&q=80"
    return fetch_image_from_url(stock_url, width=width, height=height, cache_path=cache_path)
