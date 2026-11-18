from __future__ import annotations

from pathlib import Path
from typing import List

SERVICE_LAYERS: List[str] = ["api", "service", "storage", "clients", "models"]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
