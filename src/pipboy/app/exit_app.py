from __future__ import annotations

from .base import App
import sys
from typing import Any


class ExitApp(App):
    name = "Exit"

    def __init__(self):
        super().__init__(self.name)

    def render(self, ctx: Any) -> None:
        ctx.draw_text(10, 80, "Exit: press Return or select to close the app")

    def handle_input(self, event: Any) -> None:
        # Accept 'select' or Enter keystroke
        if event == "select" or (isinstance(event, dict) and event.get("type") == "select"):
            try:
                # Attempt graceful shutdown
                import os
                import signal
                pid = os.getpid()
                # Signal the process to exit
                os.kill(pid, signal.SIGTERM)
            except Exception:
                # Fallback to hard exit
                sys.exit(0)
