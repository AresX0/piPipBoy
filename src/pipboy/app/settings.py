from __future__ import annotations
from typing import Any
from pipboy.driver.hardware_controller import HardwareController

class SettingsApp:
    name = "Settings"

    def __init__(self, controller: HardwareController | None = None):
        self.controller = controller or HardwareController()
        self._last_status = ""

    def render(self, ctx: Any) -> None:
        # Simple textual rendering for the dev UI
        y = 50
        ctx.draw_text(10, y, "Settings:")
        y += 20
        camera_state = getattr(self.controller, "_camera_enabled", False)
        ctx.draw_text(10, y, f"Camera: {'On' if camera_state else 'Off'}")
        y += 20
        ctx.draw_text(10, y, "Fan: use input {'set_fan'} with value 0-100")
        y += 20
        ctx.draw_text(10, y, "LED: patterns: off, solid, breathing, rainbow")
        y += 20
        if self._last_status:
            ctx.draw_text(10, y, f"Last: {self._last_status}")

    def handle_input(self, evt: Any) -> None:
        # Accept dict-style events for programmatic control in tests and remote control
        try:
            if isinstance(evt, dict):
                t = evt.get("type")
                if t == "set_fan":
                    val = evt.get("value", 0)
                    ok = self.controller.set_fan_speed(val)
                    self._last_status = f"set_fan {val} -> {ok}"
                elif t == "set_camera":
                    val = bool(evt.get("value", False))
                    ok = self.controller.set_camera_enabled(val)
                    self._last_status = f"set_camera {val} -> {ok}"
                elif t == "set_led":
                    pattern = evt.get("pattern", "off")
                    color = evt.get("color")
                    if color and isinstance(color, str) and color.startswith("#"):
                        color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
                    ok = self.controller.set_led_pattern(pattern, color)
                    self._last_status = f"set_led {pattern} -> {ok}"
                else:
                    self._last_status = f"unknown evt {t}"
        except Exception as e:
            self._last_status = f"error: {e}"