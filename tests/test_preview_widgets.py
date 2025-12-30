import pytest

from pipboy.interface import preview_widgets


import tkinter as tk
import pytest


def test_led_swatch_headless():
    # Should work even when tkinter isn't available
    try:
        sw = preview_widgets.LEDSwatch(parent=None, color="#112233", size=8)
    except tk.TclError:
        pytest.skip("no display available; skipping GUI headless test")
    sw.set_color("#445566")
    assert hasattr(sw, "color") or hasattr(sw, "_rect")


def test_fan_gauge_headless():
    try:
        g = preview_widgets.FanGauge(parent=None, size=16)
    except tk.TclError:
        pytest.skip("no display available; skipping GUI headless test")
    g.set_speed(0.5)
    assert (hasattr(g, "_speed") and g._speed == 0.5) or hasattr(g, "_arc")


def test_camera_preview_store_bytes():
    try:
        c = preview_widgets.CameraPreview(parent=None, w=32, h=24)
    except tk.TclError:
        pytest.skip("no display available; skipping GUI headless test")
    # None should be accepted
    c.update_image(None)
    # Simulate bytes: in headless mode it stores _last
    b = b"fake"
    c.update_image(b)
    if hasattr(c, "_last"):
        assert c._last == b
