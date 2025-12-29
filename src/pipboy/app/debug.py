"""Debug app to surface logs and diagnostic info"""
from __future__ import annotations

from .base import App


class DebugApp(App):
    def __init__(self):
        super().__init__("Debug")

    def render(self, ctx):
        ctx.draw_text(10, 80, "Debug: logs and diagnostics")
