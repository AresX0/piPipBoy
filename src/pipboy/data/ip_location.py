"""IP location provider stub

This is a stub that can be replaced by a provider that uses an offline cache or an external service (configurable).
"""
from __future__ import annotations

from typing import Optional, Tuple


class IPLocationProvider:
    def __init__(self, cache_dir: str | None = None):
        self.cache_dir = cache_dir

    def locate(self) -> Optional[Tuple[float, float]]:
        # Return None if unavailable
        return None
