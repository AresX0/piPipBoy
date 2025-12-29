"""AppManager: manage apps, tabbed home, and input routing

Provides a small, testable controller that renders the top tab bar and delegates
rendering and input to the active app.
"""
from __future__ import annotations

from typing import List, Any


class AppManager:
    def __init__(self, apps: List[Any], feedback_color: str = "#ffff66", feedback_duration: float = 0.5):
        assert apps, "At least one app required"
        self.apps = apps
        self.index = 0
        # UI feedback state and configurable appearance
        self._last_feedback_time = 0.0
        self._feedback_duration = feedback_duration
        self._feedback_color = feedback_color

    @property
    def current(self):
        return self.apps[self.index]

    def next(self):
        self.index = (self.index + 1) % len(self.apps)
        self.feedback()

    def prev(self):
        self.index = (self.index - 1) % len(self.apps)
        self.feedback()

    def feedback(self) -> None:
        import time

        self._last_feedback_time = time.monotonic()

    def _is_feedback_active(self) -> bool:
        import time

        return (time.monotonic() - self._last_feedback_time) < self._feedback_duration

    def feedback_phase(self) -> float:
        """Return a phase value in [0, 1) representing the feedback's progress relative to its duration.
        Returns 0.0 if feedback is not active."""
        import time

        if not self._is_feedback_active():
            return 0.0
        return (time.monotonic() - self._last_feedback_time) / self._feedback_duration

    def handle_input(self, event: str) -> None:
        if event == "next":
            self.next()
        elif event == "prev":
            self.prev()
        else:
            # Forward to app-specific handler
            try:
                self.current.handle_input(event)
            except Exception:
                pass

    def render(self, ctx: Any) -> None:
        # Draw tab bar
        x = 10
        y = 10
        fb_active = self._is_feedback_active()
        for i, app in enumerate(self.apps):
            label = getattr(app, "name", f"App{i}")[:8]
            if i == self.index:
                fg = "#99ff66" if not fb_active else self._feedback_color
            else:
                fg = "#66aa44"
            # Allow TkInterface to override tab fg (pulse effect)
            if hasattr(ctx, "_tab_fg_override") and ctx._tab_fg_override is not None and i == self.index:
                fg = ctx._tab_fg_override
            ctx.draw_text(x, y, label, fg=fg)
            x += 60
        # Delegate to active app
        if hasattr(self.current, "render"):
            self.current.render(ctx)
