"""Small Tk preview widgets used in the dev UI (LED swatch, camera preview, fan gauge).

These are intentionally minimal and headless-safe for unit testing.
"""
from __future__ import annotations
from typing import Optional

try:
    import tkinter as tk
    from PIL import Image, ImageTk
except Exception:
    # Headless / PIL missing: provide minimal shims for tests
    tk = None


class LEDSwatch:
    def __init__(self, parent, color="#000000", size=32):
        if tk is None:
            self.color = color
            self.size = size
            return
        self.frame = tk.Frame(parent, width=size, height=size)
        self.canvas = tk.Canvas(self.frame, width=size, height=size, highlightthickness=0)
        self.canvas.pack()
        self.size = size
        self._rect = self.canvas.create_rectangle(0, 0, size, size, fill=color)

    def set_color(self, color: str):
        if tk is None:
            self.color = color
            return
        self.canvas.itemconfig(self._rect, fill=color)


class CameraPreview:
    def __init__(self, parent, w=160, h=120):
        if tk is None:
            self._placeholder = True
            return
        self.frame = tk.Frame(parent)
        self.label = tk.Label(self.frame, text="No Image")
        self.label.pack()
        self.w = w
        self.h = h
        self._photo = None

    def update_image(self, img_bytes: Optional[bytes]):
        if tk is None:
            # store marker for tests
            self._last = img_bytes
            return
        if img_bytes is None:
            self.label.config(text="No Image")
            return
        try:
            image = Image.open(io.BytesIO(img_bytes))
            image = image.resize((self.w, self.h))
            self._photo = ImageTk.PhotoImage(image)
            self.label.config(image=self._photo, text="")
        except Exception:
            self.label.config(text="Invalid Image")


class FanGauge:
    def __init__(self, parent, size=64):
        if tk is None:
            self._speed = 0
            return
        self.frame = tk.Frame(parent)
        self.canvas = tk.Canvas(self.frame, width=size, height=size)
        self.canvas.pack()
        self.size = size
        self._arc = self.canvas.create_arc(2, 2, size - 2, size - 2, start=90, extent=0, fill="green")

    def set_speed(self, percent: float):
        capped = max(0.0, min(1.0, percent))
        if tk is None:
            self._speed = capped
            return
        extent = 360 * capped
        self.canvas.itemconfig(self._arc, extent=extent)
