from __future__ import annotations

from typing import Any


class DisplayApp:
    """Display-related controls (brightness, rotation).

    Minimal stub implementation used for UI. Exposes:
      - {'rotate': degrees}
      - {'brightness': 0-100}
    """

    name = "Display"

    def __init__(self, controller: Any = None):
        self.controller = controller
        self._brightness = 100
        self._rotation = 0

    def render(self, ctx):
        pass

    def handle_input(self, evt):
        if isinstance(evt, dict) and 'brightness' in evt:
            try:
                b = int(evt['brightness'])
                self._brightness = max(0, min(100, b))
                return True
            except Exception:
                return False
        if isinstance(evt, dict) and 'rotate' in evt:
            try:
                r = int(evt['rotate'])
                self._rotation = r % 360
                return True
            except Exception:
                return False
        if evt == 'select':
            return {'action': 'show_display_controls'}
        return False
