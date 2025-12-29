"""Clock app
"""
from __future__ import annotations

import time
from .base import SelfUpdatingApp


class ClockApp(SelfUpdatingApp):
    def __init__(self):
        super().__init__("Clock")

    def render(self, ctx):
        ctx.draw_text(10, 80, time.strftime("%Y-%m-%d %H:%M:%S"))

    def needs_update(self):
        return True

    def update(self):
        # Could sync RTC here
        pass
