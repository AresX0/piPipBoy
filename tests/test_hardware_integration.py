import os
import platform
import pytest

from pipboy.driver import backends


def is_raspberry_pi() -> bool:
    """Detect whether tests are running on a Raspberry Pi.

    Primary detection: read /proc/device-tree/model on Linux and look for
    'raspberry' in the model string. If that fails, allow an explicit opt-in
    via environment variable `RUN_PI_HARDWARE_TESTS=1` (useful for forcing tests
    on custom hardware or during local experimentation).
    """
    if platform.system() == "Linux":
        try:
            with open("/proc/device-tree/model", "rb") as f:
                model = f.read().lower()
                if b"raspberry" in model or b"raspberry pi" in model:
                    return True
        except Exception:
            # Fall back to env var override if model file not readable
            pass

    val = os.environ.get("RUN_PI_HARDWARE_TESTS")
    if val and val.lower() in ("1", "true", "yes", "on"):
        return True

    # Default: not a Raspberry Pi
    return False


pytestmark = pytest.mark.skipif(not is_raspberry_pi(), reason="Raspberry Pi hardware tests skipped; set RUN_PI_HARDWARE_TESTS=1 to force")


def test_fan_backend_operates():
    fb = backends.create_fan_backend(18)
    assert fb is not None, "Fan backend not available"
    # Try a simple operation; different backends expose different APIs
    try:
        if hasattr(fb, "value"):
            fb.value = 0.3
        elif hasattr(fb, "ChangeDutyCycle"):
            fb.ChangeDutyCycle(30)
        else:
            # Best effort
            fb.start(30)
    except Exception as e:
        pytest.fail(f"Failed to operate fan backend: {e}")


def test_led_backend_operates():
    lb = backends.create_led_backend()
    assert lb is not None, "LED backend not available"
    # Basic smoke test: try to set a pixel if API exists
    try:
        if hasattr(lb, "setPixelColor"):
            lb.setPixelColor(0, 0x00FF00)
            lb.show()
        elif hasattr(lb, "begin"):
            # Already began in factory; nothing else to do
            pass
    except Exception as e:
        pytest.fail(f"Failed to operate LED backend: {e}")


def test_oled_backend_operates():
    ob = backends.create_oled_backend()
    assert ob is not None, "OLED backend not available"
    try:
        if hasattr(ob, "draw_text"):
            ob.draw_text(0, 0, "TEST")
            ob.clear()
    except Exception as e:
        pytest.fail(f"Failed to operate OLED backend: {e}")


def test_camera_backend_operates():
    cb = backends.create_camera_backend()
    assert cb is not None, "Camera backend not available"
    try:
        img = cb.capture()
        assert isinstance(img, (bytes, bytearray))
    except Exception as e:
        pytest.fail(f"Failed to capture image from camera backend: {e}")
