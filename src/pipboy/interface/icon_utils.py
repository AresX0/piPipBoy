from __future__ import annotations

import base64
from pathlib import Path
from typing import Iterable, Optional

# Small 1x1 transparent PNG (base64)
_TRANSPARENT_PNG = (
    b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/w8AAoMBgkUq3aUAAAAASUVORK5CYII='
)


def find_or_create_icon(name: str, search_dirs: Iterable[Path]) -> Optional[Path]:
    """Find an icon for `name` (case-insensitive) in search_dirs.

    If no existing icon is found, create a small placeholder PNG named
    '<lowername>.png' in the first writable search dir and return that path.
    Returns None if no search_dir is writable.
    """
    name = name or ""
    candidates = [f"{name}.png", f"{name.lower()}.png", f"{name.capitalize()}.png", f"{name.upper()}.png"]
    for d in search_dirs:
        d = Path(d)
        try:
            if not d.exists():
                continue
        except Exception:
            continue
        for p in d.iterdir():
            if not p.is_file():
                continue
            if p.suffix.lower() != ".png":
                continue
            if p.name.lower() == name.lower() + ".png" or p.name in candidates:
                return p
        # case-insensitive glob: check if any file name matches ignoring case
        for p in d.iterdir():
            if p.is_file() and p.suffix.lower() == ".png":
                if p.name.lower().startswith(name.lower()):
                    return p
    # Not found — try to create placeholder in first writable dir
    for d in search_dirs:
        try:
            d = Path(d)
            if not d.exists():
                d.mkdir(parents=True, exist_ok=True)
            dest = d / (name.lower() + ".png")
            with open(dest, "wb") as f:
                f.write(base64.b64decode(_TRANSPARENT_PNG))
            return dest
        except Exception:
            continue
    return None
