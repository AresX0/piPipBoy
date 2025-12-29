"""Radio / audio player (optional)
"""
from __future__ import annotations

from .base import App


class RadioApp(App):
    def __init__(self):
        super().__init__("Radio")
        self.playing = False

    def render(self, ctx):
        ctx.draw_text(10, 80, f"Radio: {'PLAYING' if self.playing else 'STOPPED'}")

    def handle_input(self, event):
        if event == "toggle":
            self.playing = not self.playing
