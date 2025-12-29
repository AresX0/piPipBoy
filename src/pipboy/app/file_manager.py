"""File manager app (minimal)
"""
from __future__ import annotations

from .base import App


class FileManagerApp(App):
    def __init__(self):
        super().__init__("FileManager")
        self.cwd = "."

    def render(self, ctx):
        ctx.draw_text(10, 80, f"FileManager: {self.cwd}")

    def handle_input(self, event):
        pass
