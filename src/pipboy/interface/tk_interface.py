"""Tk-based UI for development and testing (desktop fallback)
"""
# Minimal, testable Tk interface used for dev mode
from __future__ import annotations

import tkinter as tk
from pathlib import Path
import yaml
from typing import Any
import math


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return '#%02x%02x%02x' % rgb


def _blend_hex(h1: str, h2: str, factor: float) -> str:
    """Linearly blend two hex colors by factor in [0,1]."""
    r1, g1, b1 = _hex_to_rgb(h1)
    r2, g2, b2 = _hex_to_rgb(h2)
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    return _rgb_to_hex((r, g, b))


class TkInterface:
    def __init__(self, config_path: Path, sensors: dict | None = None):
        self.config_path = config_path
        self.sensors = sensors or {}
        self.root = tk.Tk()
        self.root.title("piPipBoy - DEV MODE")
        self.canvas = tk.Canvas(self.root, width=480, height=320, bg="#001100")
        self.canvas.pack()
        self.load_config()
        # Create app manager with basic apps; inject sensors into EnvironmentApp
        from pipboy.app.file_manager import FileManagerApp
        from pipboy.app.map import MapApp
        from pipboy.app.environment import EnvironmentApp
        from pipboy.app.clock import ClockApp
        from pipboy.app.radio import RadioApp
        from pipboy.app.update import UpdateApp
        from pipboy.app.debug import DebugApp
        from .app_manager import AppManager

        self.app_manager = AppManager([
            FileManagerApp(),
            MapApp(),
            EnvironmentApp(sensors=self.sensors),
            ClockApp(),
            RadioApp(),
            UpdateApp(),
            DebugApp(),
        ])

    def load_config(self) -> None:
        try:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f)
        except Exception:
            self.config = {"theme": "green"}

    def draw_text(self, x: int, y: int, text: str, fg: str = "#99ff66") -> None:
        self.canvas.create_text(x, y, anchor="nw", text=text, fill=fg, font=("Courier", 12))

    def _tick(self):
        # Render once per tick with optional pulse feedback when app_manager indicates
        theme = self.config.get("themes", {}).get(self.config.get("theme", "green"))
        fg = theme.get("fg", "#99ff66") if theme else "#99ff66"
        bg = theme.get("bg", "#001100") if theme else "#001100"
        fb_color = theme.get("feedback_fg", "#ffff66") if theme else "#ffff66"
        fb_duration = theme.get("feedback_duration", 0.5) if theme else 0.5

        self.canvas.config(bg=bg)
        self.canvas.delete("all")
        self.draw_text(10, 10, "piPipBoy - DEV MODE", fg=fg)

        # If feedback is active, compute pulsing blend between fg and fb_color
        if self.app_manager._is_feedback_active():
            # phase in [0,1)
            phase = self.app_manager.feedback_phase()
            # create a smooth pulse (sinusoidal)
            pulse = 0.5 * (1 + math.sin(2 * math.pi * phase))
            current_fg = _blend_hex(fg, fb_color, pulse)
            # override drawing of tab labels by temporarily storing original draw_text
            self._tab_fg_override = current_fg
            # render tabs and apps
            self.app_manager.render(self)
            self._tab_fg_override = None
        else:
            # delegate rendering normally
            self.app_manager.render(self)

        # schedule next tick; use theme speed or default
        self.root.after(int(fb_duration * 1000 / 10) or 100, self._tick)

    def run(self) -> None:
        # Bind keys for switching
        self.root.bind("<Left>", lambda e: self.app_manager.handle_input("prev"))
        self.root.bind("<Right>", lambda e: self.app_manager.handle_input("next"))
        self.root.bind("<Return>", lambda e: self.app_manager.handle_input("select"))
        self._tick()
        self.root.mainloop()
