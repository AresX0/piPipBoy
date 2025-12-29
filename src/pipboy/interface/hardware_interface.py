"""HardwareInterface: wire display + input to AppManager for Pi hardware

Provides a small loop runner and a run_once method for testability.
"""
from __future__ import annotations

import time
from typing import Any


class HardwareInterface:
    def __init__(self, display: Any, inputs: Any, app_manager: Any, tick: float = 0.5):
        self.display = display
        self.inputs = inputs
        self.app_manager = app_manager
        self.tick = tick
        self._wired = False

    def initialize(self) -> None:
        # initialize display
        try:
            self.display.initialize()
        except Exception:
            pass
        # wire inputs: expect inputs to have `on(name, handler)` method
        try:
            self.inputs.on("next", lambda: self.app_manager.handle_input("next"))
            self.inputs.on("prev", lambda: self.app_manager.handle_input("prev"))
            self.inputs.on("select", lambda: self.app_manager.handle_input("select"))
            # Rotary encoder mappings
            self.inputs.on("rot_left", lambda: self.app_manager.handle_input("prev"))
            self.inputs.on("rot_right", lambda: self.app_manager.handle_input("next"))
            # Short press == select, long press == back
            self.inputs.on("rot_push", lambda: self.app_manager.handle_input("select"))
            self.inputs.on("rot_push_short", lambda: self.app_manager.handle_input("select"))
            self.inputs.on("rot_push_long", lambda: self.app_manager.handle_input("back"))
        except Exception:
            # If inputs can't be wired, ignore; dev mode will fallback
            pass
        self._wired = True

    def run_once(self) -> None:
        # Single tick: render and update
        # clear display
        try:
            self.display.clear()
        except Exception:
            pass
        # Render current view into display via app_manager.render(ctx)
        try:
            self.app_manager.render(self.display)
        except Exception:
            pass
        # Flush to device
        try:
            self.display.update()
        except Exception:
            pass

    def run(self) -> None:
        self.initialize()
        while True:
            self.run_once()
            time.sleep(self.tick)
