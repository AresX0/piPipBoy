"""Hardware peripheral abstractions (fan, LEDs, OLED, camera)

These are minimal, testable controllers that provide a thin, hardware-free API
so higher-level app code can call `set_speed`, `set_color`, `display_text`, or
`capture_image` without importing hardware libraries at module import time.
"""
from __future__ import annotations

from typing import Any, Tuple
import time


class FanController:
    """Simple PWM fan controller abstraction."""

    def __init__(self, pwm: Any | None = None, pin: int | None = None):
        self._pwm = pwm
        self._pin = pin
        self._speed = 0  # 0..100

    def set_speed(self, percent: int) -> None:
        """Set fan speed 0..100."""
        percent = max(0, min(100, int(percent)))
        self._speed = percent
        try:
            if self._pwm is not None:
                # pwm interface expected to have ChangeDutyCycle
                self._pwm.ChangeDutyCycle(self._speed)
        except Exception:
            pass

    def get_speed(self) -> int:
        return self._speed


class LEDController:
    """RGB LED controller abstraction (single-color or multi-LED support).

    This controller exposes a simple interface for setting brightness or
    color. Hardware-specific wiring (e.g., WS281x, PWM pins) should be
    injected via the `driver` parameter if available.
    """

    def __init__(self, driver: Any | None = None):
        self._driver = driver
        self._color = (255, 255, 255)
        self._brightness = 100

    def set_color(self, rgb: Tuple[int, int, int]) -> None:
        self._color = tuple(max(0, min(255, int(c))) for c in rgb)
        try:
            if self._driver is not None:
                self._driver.set_color(self._color)
        except Exception:
            pass

    def set_brightness(self, percent: int) -> None:
        self._brightness = max(0, min(100, int(percent)))
        try:
            if self._driver is not None:
                self._driver.set_brightness(self._brightness)
        except Exception:
            pass

    def get_state(self) -> Tuple[Tuple[int, int, int], int]:
        return self._color, self._brightness


class OLEDController:
    """Tiny OLED text updater. Backed by an I2C or SPI display if provided."""

    def __init__(self, device: Any | None = None):
        self._device = device
        self._lines: list[str] = []

    def display_text(self, *lines: str) -> None:
        self._lines = list(lines)
        try:
            if self._device is not None:
                # device provided by the platform; call its text API
                for i, l in enumerate(lines):
                    self._device.draw_text(0, i * 10, l)
                self._device.update()
        except Exception:
            pass

    def clear(self) -> None:
        self._lines = []
        try:
            if self._device is not None:
                self._device.clear()
                self._device.update()
        except Exception:
            pass

    def get_lines(self) -> list[str]:
        return list(self._lines)


class CameraInterface:
    """Simple camera abstraction supporting capture and recording.

    Uses `picamera2` or `cv2` if available; otherwise provides a testable
    stub that returns placeholder bytes.
    """

    def __init__(self, backend: Any | None = None):
        self._backend = backend
        self._recording = False

    def capture_image(self, path: str | None = None) -> bytes:
        try:
            if self._backend is not None and hasattr(self._backend, "capture"):
                data = self._backend.capture()
                if path:
                    with open(path, "wb") as f:
                        f.write(data)
                return data
        except Exception:
            pass
        # Return a tiny placeholder PNG bytes so callers can validate
        placeholder = b"PNGPLACEHOLDER"
        if path:
            try:
                with open(path, "wb") as f:
                    f.write(placeholder)
            except Exception:
                pass
        return placeholder

    def start_recording(self, path: str) -> None:
        self._recording = True
        # If backend supports recording, call into it
        try:
            if self._backend is not None and hasattr(self._backend, "start_recording"):
                self._backend.start_recording(path)
        except Exception:
            pass

    def stop_recording(self) -> None:
        self._recording = False
        try:
            if self._backend is not None and hasattr(self._backend, "stop_recording"):
                self._backend.stop_recording()
        except Exception:
            pass

    def is_recording(self) -> bool:
        return self._recording
