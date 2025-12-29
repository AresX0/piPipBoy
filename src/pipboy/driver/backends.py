"""Optional hardware backend discovery and factory utilities.

Provide helpers that attempt to create real hardware drivers when running on a
Raspberry Pi with the proper libraries installed. All imports are attempted at
runtime and failures fall back to None so code remains testable on CI.

Optional runtime dependencies (install on a Pi if you want hardware support):
- picamera2 (camera support) or opencv-python (cv2 fallback)
- rpi_ws281x (WS281x LED strips)
- luma.oled (I2C/OLED text displays) and pillow (PIL)
- gpiozero or RPi.GPIO (PWM / GPIO control)

Install example (on Raspberry Pi):
    sudo apt-get update && sudo apt-get install -y libjpeg-dev libopenjp2-7-dev
    pip install picamera2 opencv-python rpi_ws281x luma.oled gpiozero pillow

See docs/OPTIONAL-HARDWARE.md for more details and wiring notes.
"""
from __future__ import annotations
from typing import Any, Tuple


def create_fan_backend(pin: int | None) -> Any | None:
    """Try to create a PWM-based fan backend.

    Returns an object with ChangeDutyCycle(percent) if available, otherwise
    returns None.
    """
    if pin is None:
        return None
    try:
        from gpiozero import PWMOutputDevice

        return PWMOutputDevice(pin)
    except Exception:
        try:
            import RPi.GPIO as GPIO

            # Setup a simple PWM channel wrapper
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.OUT)
            pwm = GPIO.PWM(pin, 25000)  # 25kHz
            pwm.start(0)
            return pwm
        except Exception:
            return None


def create_led_backend() -> Any | None:
    """Try to create an LED (WS281x) backend if rpi_ws281x is available."""
    try:
        from rpi_ws281x import PixelStrip, Color

        # Default strip config; callers should configure length/channel as needed
        strip = PixelStrip(8, 18)  # 8 LEDs, GPIO18
        strip.begin()
        return strip
    except Exception:
        return None


def create_oled_backend() -> Any | None:
    """Try to create a luma.oled backend for a small text display."""
    try:
        from luma.core.interface.serial import i2c
        from luma.oled.device import ssd1306

        serial = i2c(port=1, address=0x3C)
        device = ssd1306(serial)

        class LumaWrapper:
            def __init__(self, dev):
                self.dev = dev

            def draw_text(self, x, y, text):
                from PIL import Image, ImageDraw, ImageFont

                img = Image.new("1", self.dev.size)
                draw = ImageDraw.Draw(img)
                font = ImageFont.load_default()
                draw.text((x, y), text, font=font, fill=255)
                self.dev.display(img)

            def clear(self):
                self.dev.clear()
                self.dev.show()

        return LumaWrapper(device)
    except Exception:
        return None


def create_camera_backend() -> Any | None:
    """Try to provide a camera backend. Prefer picamera2, fallback to cv2.

    The returned backend is expected to have `capture()` method returning bytes,
    and optional start_recording/stop_recording methods.
    """
    try:
        # picamera2 style
        from picamera2 import Picamera2

        class Picamera2Backend:
            def __init__(self):
                self.cam = Picamera2()
                self.cam.configure(self.cam.create_preview_configuration({"size": (640, 480)}))
                self.cam.start()

            def capture(self):
                arr = self.cam.capture_array()
                # encode as JPEG via cv2
                try:
                    import cv2

                    ret, buf = cv2.imencode(".jpg", arr)
                    if ret:
                        return buf.tobytes()
                except Exception:
                    return b"PICAMERA_PLACEHOLDER"

            def start_recording(self, path):
                # picamera2 supports recording; real implementation omitted
                pass

            def stop_recording(self):
                pass

        return Picamera2Backend()
    except Exception:
        try:
            import cv2

            class CV2Backend:
                def __init__(self):
                    self.cap = cv2.VideoCapture(0)

                def capture(self):
                    ret, frame = self.cap.read()
                    if not ret:
                        return b"CV2_NO_FRAME"
                    ret, buf = cv2.imencode(".jpg", frame)
                    if ret:
                        return buf.tobytes()
                    return b"CV2_ENCODE_FAIL"

                def start_recording(self, path):
                    # Omitted: implement VideoWriter
                    pass

                def stop_recording(self):
                    pass

            return CV2Backend()
        except Exception:
            return None