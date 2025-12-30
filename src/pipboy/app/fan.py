from __future__ import annotations

from typing import Any


class FanApp:
    """Simple Fan control app.

    Expected inputs:
      - {'set_fan': <percent>} to set fan speed (0-100)
    """

    name = "Fan"

    def __init__(self, controller: Any = None):
        self.controller = controller
        self._last = None

    def render(self, ctx):
        # Minimal rendering: apps are free to draw into ctx (Canvas-like)
        pass

    def handle_input(self, evt):
        # Accept a dict with 'set_fan' or a simple 'select' to request UI
        if isinstance(evt, dict) and 'set_fan' in evt:
            try:
                val = float(evt['set_fan'])
            except Exception:
                return False
            self._last = val
            if self.controller:
                return bool(self.controller.set_fan_speed(val))
            return True
        if evt == 'select':
            # In a real UI, would show controls; here we just return a hint
            return {'action': 'show_fan_control'}
        return False
