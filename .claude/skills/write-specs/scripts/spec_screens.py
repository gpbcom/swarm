"""Screens: PNG files, their HTML mock-ups, and rendering mock-ups with a headless browser."""

from __future__ import annotations

import hashlib
import os
import shutil
import struct
import subprocess
import tempfile
import zlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image

from spec_model import COMPONENTS_CSS, IDENTITY_CSS, MOCKUPS, SCREENS

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SOURCE_KEY = "spec-source"
BROWSERS = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")
PALETTE_COLOURS = 256
PALETTE_TYPE = 3


def png_info(path: Path) -> Tuple[Optional[Tuple[int, int]], Dict[str, str]]:
    data = path.read_bytes()
    if data[:8] != PNG_SIGNATURE:
        return None, {}
    position, size, texts = 8, None, {}
    while position + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[position:position + 8])
        body = data[position + 8:position + 8 + length]
        if kind == b"IHDR":
            size = struct.unpack(">II", body[:8])
        elif kind == b"tEXt":
            key, _, value = body.partition(b"\0")
            texts[key.decode("latin-1")] = value.decode("latin-1")
        elif kind == b"IEND":
            break
        position += 12 + length
    return size, texts


def png_colour_type(path: Path) -> Optional[int]:
    data = path.read_bytes()[:26]
    return data[25] if data[:8] == PNG_SIGNATURE and data[12:16] == b"IHDR" else None


def palettise(path: Path) -> None:
    texts = png_info(path)[1]
    with Image.open(path) as image:
        reduced = image.convert("RGB").quantize(colors=PALETTE_COLOURS, dither=Image.Dither.NONE)
    reduced.save(path, "PNG", optimize=True)
    for key, value in texts.items():
        png_set_text(path, key, value)


def png_set_text(path: Path, key: str, value: str) -> None:
    data = path.read_bytes()
    chunks: List[bytes] = []
    position = 8
    while position + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[position:position + 8])
        chunk = data[position:position + 12 + length]
        body = data[position + 8:position + 8 + length]
        position += 12 + length
        if kind == b"tEXt" and body.partition(b"\0")[0] == key.encode("latin-1"):
            continue
        if kind == b"IEND":
            text = key.encode("latin-1") + b"\0" + value.encode("latin-1")
            crc = zlib.crc32(b"tEXt" + text) & 0xFFFFFFFF
            chunks.append(struct.pack(">I", len(text)) + b"tEXt" + text + struct.pack(">I", crc))
        chunks.append(chunk)
    path.write_bytes(data[:8] + b"".join(chunks))


def source_hash(html: Path, mode: str) -> str:
    digest = hashlib.sha256(mode.encode("ascii") + html.read_bytes())
    for css in (IDENTITY_CSS, COMPONENTS_CSS):
        digest.update(css.read_bytes() if css.is_file() else b"")
    return digest.hexdigest()


def png_for(html: Path, mode: str) -> Path:
    suffix = ".dark.png" if mode == "dark" else ".png"
    return SCREENS / html.relative_to(MOCKUPS).parent / (html.stem + suffix)


def mode_of(png: Path) -> str:
    return "dark" if png.name.endswith(".dark.png") else "light"


def mockup_for(png: Path) -> Path:
    stem = png.name[: -len(".dark.png")] if mode_of(png) == "dark" else png.stem
    return MOCKUPS / png.relative_to(SCREENS).parent / f"{stem}.html"


def screen_pngs() -> List[Path]:
    return sorted(p for p in SCREENS.rglob("*.png") if MOCKUPS not in p.parents) if SCREENS.is_dir() else []


def mockups() -> List[Path]:
    return sorted(MOCKUPS.rglob("*.html")) if MOCKUPS.is_dir() else []


def find_browser() -> Optional[str]:
    configured = os.environ.get("SPECS_BROWSER")
    if configured:
        return configured
    return next((found for name in BROWSERS if (found := shutil.which(name))), None)


def render(browser: str, html: Path, size: Tuple[int, int], mode: str) -> Optional[str]:
    png = png_for(html, mode)
    png.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        command = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                   "--no-default-browser-check", "--force-device-scale-factor=1", f"--user-data-dir={profile}",
                   f"--blink-settings=preferredColorScheme={0 if mode == 'dark' else 1}",
                   f"--window-size={size[0]},{size[1]}", "--virtual-time-budget=3000", f"--screenshot={png}",
                   html.as_uri()]
        result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
    if not png.is_file():
        return f"the browser wrote no PNG (exit {result.returncode}): {result.stderr.strip()[-300:]}"
    actual, _ = png_info(png)
    if actual != size:
        return f"rendered at {actual}, expected {size[0]} x {size[1]}."
    png_set_text(png, SOURCE_KEY, source_hash(html, mode))
    palettise(png)
    return None
