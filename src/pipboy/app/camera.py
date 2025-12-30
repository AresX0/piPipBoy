from __future__ import annotations

from typing import Any


class CameraApp:
    """Simple Camera control app.

    Expected inputs:
      - {'enable': True|False} to enable/disable camera
      - 'select' to toggle camera state
    """

    name = "Camera"

    def __init__(self, controller: Any = None):
        self.controller = controller
        self._enabled = False

    def render(self, ctx):
        pass

    def handle_input(self, evt):
        if isinstance(evt, dict) and 'enable' in evt:
            enable = bool(evt['enable'])
            self._enabled = enable
            if self.controller:
                return bool(self.controller.set_camera_enabled(enable))
            return True
        if evt == 'select':
            self._enabled = not self._enabled
            if self.controller:
                return bool(self.controller.set_camera_enabled(self._enabled))
            return True
        return False
