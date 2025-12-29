from __future__ import annotations

from .base import App


class PeripheralsApp(App):
    def __init__(self):
        super().__init__("Peripherals")
        # internal state
        self._fan_target = 0
        self._led_brightness = 100
        self._oled_lines = ["", ""]
        self._camera_status = "idle"

    def render(self, ctx):
        ctx.draw_text(10, 60, f"Fan: {self._fan_target}%")
        ctx.draw_text(10, 80, f"LED Brightness: {self._led_brightness}%")
        ctx.draw_text(10, 100, f"OLED: {self._oled_lines[:2]}")
        ctx.draw_text(10, 120, f"Camera: {self._camera_status}")
        ctx.draw_text(10, 140, "Use select to toggle capture, up/down to set fan, left/right LED")

    def handle_input(self, event):
        try:
            pm = self.app_manager.peripherals
        except Exception:
            pm = {}
        fan = pm.get("fan") if pm else None
        leds = pm.get("leds") if pm else None
        oled = pm.get("oled") if pm else None
        cam = pm.get("camera") if pm else None

        if event == "up":
            self._fan_target = min(100, self._fan_target + 10)
            if fan:
                fan.set_speed(self._fan_target)
        elif event == "down":
            self._fan_target = max(0, self._fan_target - 10)
            if fan:
                fan.set_speed(self._fan_target)
        elif event == "left":
            self._led_brightness = max(0, self._led_brightness - 10)
            if leds:
                leds.set_brightness(self._led_brightness)
        elif event == "right":
            self._led_brightness = min(100, self._led_brightness + 10)
            if leds:
                leds.set_brightness(self._led_brightness)
        elif event == "select":
            # toggle camera capture (single image)
            if cam:
                self._camera_status = "capturing"
                cam.capture_image()
                self._camera_status = "idle"
        elif event == "rot_right":
            # Update OLED sample text
            self._oled_lines = [f"T:{self._fan_target}%", f"L:{self._led_brightness}%"]
            if oled:
                oled.display_text(*self._oled_lines)
        elif event == "rot_left":
            if oled:
                oled.clear()
            self._oled_lines = ["", ""]
        else:
            pass
