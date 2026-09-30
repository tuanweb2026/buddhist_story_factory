import os
import yaml
from pathlib import Path
from typing import Any, Dict


def load_config(config_path: str = "config/factory.yaml") -> Dict[str, Any]:
    path = Path(config_path)
    if not path.is_absolute():
        base_dir = Path(__file__).resolve().parent.parent.parent
        path = base_dir / config_path
    
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
        
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dirs(base_path: str = "data"):
    subdirs = [
        "inbox", "discovery", "research", "scoring", "stories",
        "verified", "scripts", "visuals", "audio", "rendered",
        "qa", "publishing", "archive"
    ]
    base = Path(base_path)
    for s in subdirs:
        (base / s).mkdir(parents=True, exist_ok=True)
