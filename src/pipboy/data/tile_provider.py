"""Tile provider stub for map app

No external network calls; extension points allow plugging an offline tile cache or remote service.
"""
from __future__ import annotations

from typing import Tuple


class TileProvider:
    def __init__(self, cache_dir: str | None = None):
        self.cache_dir = cache_dir

    def get_tile(self, z: int, x: int, y: int) -> bytes | None:
        """Return raw tile image bytes if available, else None.
        Override to call offline cache or fetch from configured provider.
        """
        return None
