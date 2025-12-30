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
    def __init__(self, config_path: Path, sensors: dict | None = None, fullscreen: bool | None = None):
        """Tk-based development interface.

        Args:
            config_path: Path to the YAML config file
            sensors: optional sensor dict injected into EnvironmentApp
            fullscreen: override config to force fullscreen mode; None to use config
        """
        self.config_path = config_path
        self.sensors = sensors or {}
        # Create root early so tests can monkeypatch attributes
        self.root = tk.Tk()
        self.root.title("piPipBoy - DEV MODE")
        # Increase canvas to 800x600 (user requested)
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="#001100")
        self.canvas.pack()
        self.root.update()
        self.load_config()
        # Place tabs/icons at the bottom by default, allow config override
        ui_conf = self.config.get("ui", {}) if isinstance(self.config, dict) else {}
        self.tab_at_bottom = ui_conf.get("tab_at_bottom", True)
        # Print startup diagnostics to the GUI log so the launcher can confirm config
        try:
            print(f"STARTUP: canvas={self.canvas['width']}x{self.canvas['height']} tab_at_bottom={self.tab_at_bottom}")
        except Exception:
            pass

        # Determine fullscreen preference: explicit arg > config file
        ui_conf = self.config.get("ui", {}) if isinstance(self.config, dict) else {}
        fullscreen_pref = fullscreen if fullscreen is not None else ui_conf.get("fullscreen", False)
        if fullscreen_pref:
            try:
                self.root.attributes("-fullscreen", True)
            except Exception:
                # Fallback for platforms where -fullscreen is unsupported
                try:
                    self.root.state("zoomed")
                except Exception:
                    pass

        # Load available icons (best-effort) from either src/resources/icons or repo-root resources/icons
        self.icons: dict[str, Any] = {}
        self._load_icons()


        # Touch / click support
        ui_conf = self.config.get("ui", {}) if isinstance(self.config, dict) else {}
        self.touch_enabled = ui_conf.get("touch", False)
        self.touch_target = int(ui_conf.get("touch_target", 48))
        # Bind mouse/touch events for dev UI
        try:
            self.root.bind("<Button-1>", self._on_click)
            self.root.bind("<ButtonPress-1>", self._on_touch_start)
            self.root.bind("<B1-Motion>", self._on_touch_move)
            self.root.bind("<ButtonRelease-1>", self._on_touch_end)
        except Exception:
            # Ignore if binding not supported in test environments
            pass

        # Touch gesture state
        self._touch_start = None
        self._touch_last = None
        # Create app manager with basic apps; inject sensors into EnvironmentApp
        from pipboy.app.file_manager import FileManagerApp
        from pipboy.app.map import MapApp
        from pipboy.app.environment import EnvironmentApp
        from pipboy.app.clock import ClockApp
        from pipboy.app.radio import RadioApp
        from pipboy.app.update import UpdateApp
        from pipboy.app.debug import DebugApp
        from pipboy.app.settings import SettingsApp
        from .app_manager import AppManager

        theme = self.config.get("themes", {}).get(self.config.get("theme", "green"), {})
        fb_color = theme.get("feedback_fg", "#ffff66")
        fb_duration = theme.get("feedback_duration", 0.5)
from pipboy.app.exit_app import ExitApp

            self.app_manager = AppManager([
                FileManagerApp(),
                MapApp(),
                EnvironmentApp(sensors=self.sensors),
                ClockApp(),
                RadioApp(),
                UpdateApp(),
                DebugApp(),
                SettingsApp(),
                ExitApp(),
        ], feedback_color=fb_color, feedback_duration=fb_duration)

    def load_config(self) -> None:
        try:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f) or {}
        except Exception:
            self.config = {"theme": "green"}

    def _load_icons(self) -> None:
        """Load app icons from resources/icons (best-effort).

        Search both src/resources/icons and repo-root resources/icons so user-supplied
        icons placed at project root are discovered.
        """
        try:
            candidates = [
                Path(__file__).parent.parent.parent / "resources" / "icons",
                Path(__file__).parent.parent.parent.parent / "resources" / "icons",
            ]
            for base in candidates:
                if base.exists() and base.is_dir():
                    for p in base.glob("*.png"):
                        try:
                            self.icons[p.stem] = tk.PhotoImage(file=str(p))
                        except Exception:
                            # ignore images that fail to load
                            pass
        except Exception:
            # Don't fail UI for missing icons
            pass

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
        # Title (green) per user's request
        self.draw_text(10, 10, "PiPIPBOY", fg="#99ff66")

        # Draw a tab bar background (top or bottom depending on config)
        try:
            w = self.canvas.winfo_width() or 800
            h = self.canvas.winfo_height() or 600
            if getattr(self, "tab_at_bottom", False):
                self.canvas.create_rectangle(0, h - 36, w, h, fill=bg, outline=bg)
            else:
                self.canvas.create_rectangle(0, 0, w, 36, fill=bg, outline=bg)
        except Exception:
            pass

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

    # Touch / click handlers
    def _tab_index_at(self, x: int, y: int) -> int | None:
        """Return tab index at given x,y or None if outside tab area.

        Supports tabs at the top (y in 0..36) or bottom (y in canvas_height-36..canvas_height).
        """
        try:
            if getattr(self, "tab_at_bottom", False):
                h = self.canvas.winfo_height() or 480
                if not (h - 36 <= y <= h):
                    return None
            else:
                if not (0 <= y <= 36):
                    return None
        except Exception:
            # If we can't query canvas size, fall back to top behavior
            if not (0 <= y <= 36):
                return None

        idx = (x - 10) // 60
        if idx < 0:
            return None
        if idx >= len(self.app_manager.apps):
            return None
        return int(idx)

    def _on_click(self, event) -> None:
        try:
            idx = self._tab_index_at(event.x, event.y)
            if idx is not None:
                self.app_manager.select(idx)
                return
            # Otherwise, send a generic touch event to the app
            try:
                self.app_manager.handle_input({"type": "touch", "x": event.x, "y": event.y})
            except Exception:
                pass
        except Exception:
            pass

    def _on_touch_start(self, event) -> None:
        self._touch_start = (event.x, event.y)
        self._touch_last = (event.x, event.y)

    def _on_touch_move(self, event) -> None:
        self._touch_last = (event.x, event.y)

    def _on_touch_end(self, event) -> None:
        if self._touch_start and self._touch_last:
            dx = event.x - self._touch_start[0]
            dy = event.y - self._touch_start[1]
            if abs(dx) > 40 and abs(dx) > abs(dy):
                # horizontal swipe
                if dx > 0:
                    self.app_manager.prev()
                else:
                    self.app_manager.next()
        self._touch_start = None
        self._touch_last = None
