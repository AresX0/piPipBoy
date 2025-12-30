"""Hardware controller abstraction for camera, fan and LED patterns.

Provides safe, import-guarded access to optional peripherals. Methods are
idempotent and will no-op if the underlying hardware/library isn't available.
"""
from __future__ import annotations

import threading
import time
import logging
from typing import Optional

logger = logging.getLogger("pipboy.hardware")


class HardwareController:
    def __init__(self, led_pin: int = 18, led_count: int = 16, fan_pin: int = 12):
        self.led_pin = led_pin
        self.led_count = led_count
        self.fan_pin = fan_pin

        self._led_available = False
        self._fan_available = False
        self._camera_available = False

        # runtime state
        self._fan = None
        self._strip = None
        self._led_thread = None
        self._led_stop_event = threading.Event()
        self._camera_enabled = False

        # Try imports lazily but guarded
        try:
            import rpi_ws281x as ws
            # minimal constructor deferred; create on first use
            self._ws = ws
            self._led_available = True
            logger.debug("rpi_ws281x available for LED control")
        except Exception:
            self._ws = None
            logger.debug("rpi_ws281x not available; LED control disabled")

        try:
            from gpiozero import PWMOutputDevice
            self._PWMOutputDevice = PWMOutputDevice
            # instantiate on first use
            self._fan_available = True
            logger.debug("gpiozero PWMOutputDevice available for fan control")
        except Exception:
            self._PWMOutputDevice = None
            logger.debug("gpiozero not available; fan control disabled")

        try:
            # picamera2 may or may not be available; we just detect presence
            import picamera2  # type: ignore
            self._camera_available = True
            logger.debug("Camera library (picamera2) available")
        except Exception:
            self._camera_available = False
            logger.debug("Camera library not available; camera controls disabled")

    # FAN
    def set_fan_speed(self, percent: float) -> bool:
        """Set fan speed as percentage [0,100]. Returns True if applied."""
        try:
            p = max(0.0, min(100.0, float(percent))) / 100.0
        except Exception:
            return False
        if not self._fan_available:
            logger.info("Fan control not available on this system")
            return False
        if self._fan is None:
            try:
                self._fan = self._PWMOutputDevice(self.fan_pin)
            except Exception as e:
                logger.exception("Failed to instantiate fan PWM device: %s", e)
                return False
        try:
            self._fan.value = p
            logger.info("Set fan speed to %.1f%%", p * 100)
            return True
        except Exception:
            logger.exception("Failed to set fan speed")
            return False

    # CAMERA
    def set_camera_enabled(self, enabled: bool) -> bool:
        enabled = bool(enabled)
        if not self._camera_available:
            logger.info("Camera control not available on this system")
            self._camera_enabled = False
            return False
        # For now, only store the desired state; actual camera preview handling
        # should be done by a dedicated service if needed.
        self._camera_enabled = enabled
        logger.info("Camera enabled=%s", enabled)
        return True

    # LED patterns
    def _ensure_strip(self) -> bool:
        if not self._led_available:
            return False
        if self._strip is None:
            try:
                # Construct a minimal PixelStrip-like interface using rpi_ws281x
                self._strip = self._ws.PixelStrip(self.led_count, self.led_pin)
                self._strip.begin()
            except Exception as e:
                logger.exception("Failed to initialize LED strip: %s", e)
                self._strip = None
                return False
        return True

    def set_led_pattern(self, pattern: str, color: Optional[tuple[int, int, int]] = None) -> bool:
        """Set LED pattern: 'off', 'solid', 'breathing', 'rainbow'.
        color is an (r,g,b) tuple for the 'solid' or 'breathing' base color.
        """
        pattern = (pattern or "").lower()
        logger.info("Requested LED pattern: %s", pattern)

        # Stop existing pattern thread if running
        if self._led_thread and self._led_thread.is_alive():
            self._led_stop_event.set()
            self._led_thread.join(timeout=1.0)
            self._led_stop_event.clear()

        if pattern == "off":
            if not self._ensure_strip():
                return False
            try:
                for i in range(self._strip.numPixels()):
                    self._strip.setPixelColor(i, 0)
                self._strip.show()
                return True
            except Exception:
                logger.exception("Failed to turn off LEDs")
                return False

        if pattern == "solid":
            if not self._ensure_strip():
                return False
            r, g, b = color or (255, 255, 255)
            col = self._ws.Color(r, g, b)
            try:
                for i in range(self._strip.numPixels()):
                    self._strip.setPixelColor(i, col)
                self._strip.show()
                return True
            except Exception:
                logger.exception("Failed to set solid LED color")
                return False

        if pattern in ("breathing", "rainbow"):
            if not self._ensure_strip():
                return False

            def runner():
                try:
                    if pattern == "breathing":
                        base = color or (255, 0, 0)
                        while not self._led_stop_event.is_set():
                            for f in [i / 50.0 for i in range(51)]:
                                if self._led_stop_event.is_set():
                                    break
                                r, g, b = base
                                r = int(r * f)
                                g = int(g * f)
                                b = int(b * f)
                                col = self._ws.Color(r, g, b)
                                for i in range(self._strip.numPixels()):
                                    self._strip.setPixelColor(i, col)
                                self._strip.show()
                                time.sleep(0.02)
                    else:
                        # simple rainbow cycle
                        pos = 0
                        while not self._led_stop_event.is_set():
                            for i in range(self._strip.numPixels()):
                                # generate a color wheel
                                j = (i + pos) % 255
                                # wheel: 0..255 -> color
                                if j < 85:
                                    r, g, b = (j * 3, 255 - j * 3, 0)
                                elif j < 170:
                                    j -= 85
                                    r, g, b = (255 - j * 3, 0, j * 3)
                                else:
                                    j -= 170
                                    r, g, b = (0, j * 3, 255 - j * 3)
                                col = self._ws.Color(int(r), int(g), int(b))
                                self._strip.setPixelColor(i, col)
                            self._strip.show()
                            pos = (pos + 1) % 255
                            time.sleep(0.05)
                except Exception:
                    logger.exception("LED pattern runner failed")

            self._led_thread = threading.Thread(target=runner, daemon=True)
            self._led_thread.start()
            return True

        logger.warning("Unknown LED pattern requested: %s", pattern)
        return False

    def close(self) -> None:
        # Stop LED thread
        if self._led_thread and self._led_thread.is_alive():
            self._led_stop_event.set()
            self._led_thread.join(timeout=1.0)
        # Turn off strip if we have one
        try:
            if self._strip is not None:
                for i in range(self._strip.numPixels()):
                    self._strip.setPixelColor(i, 0)
                self._strip.show()
        except Exception:
            pass
        # Close fan device
        try:
            if self._fan is not None:
                self._fan.close()
        except Exception:
            pass
