"""Map app (zoom/pan with tile provider)
"""
from __future__ import annotations

from .base import App


class MapApp(App):
    def __init__(self, tile_provider=None):
        super().__init__("Map")
        self.tile_provider = tile_provider
        self.zoom = 2
        self.center = (0.0, 0.0)
        self.recentered = False

    def render(self, ctx):
        ctx.draw_text(10, 80, f"Map: zoom={self.zoom} center={self.center}")

    def handle_input(self, event):
        # 'back' (long press) recenters the map
        if event == "back":
            self.recenter()

    def recenter(self):
        self.center = (0.0, 0.0)
        self.recentered = True
