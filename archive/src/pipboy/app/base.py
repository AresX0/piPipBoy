"""Base classes for applications

Credit: portions derived from SirLefti/piboy (MIT) — https://github.com/SirLefti/piboy
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class App:
    """Minimal app interface"""

    name: str

    def __init__(self, name: str):
        self.name = name

    def render(self, ctx: Any) -> None:
        """Render the app to the provided rendering context"""
        raise NotImplementedError

    def handle_input(self, event: Any) -> None:
        """Handle input events"""
        raise NotImplementedError


class SelfUpdatingApp(App):
    """An app that may refresh its data periodically"""

    def needs_update(self) -> bool:
        return False

    def update(self) -> None:
        pass
