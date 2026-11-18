from __future__ import annotations

from pathlib import Path

SERVICE_LAYERS: list[str] = ["api", "service", "storage", "models"]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
