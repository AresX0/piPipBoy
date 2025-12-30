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

    def select(self, index: int) -> None:
        """Select a specific app index and trigger feedback."""
        if not self.apps:
            return
        self.index = max(0, min(len(self.apps) - 1, int(index)))
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
        # Draw tab bar (top or bottom depending on ctx.tab_at_bottom)
        x = 10
        fb_active = self._is_feedback_active()

        # Determine y position based on context preference
        try:
            if hasattr(ctx, "tab_at_bottom") and ctx.tab_at_bottom and hasattr(ctx, "canvas"):
                h = ctx.canvas.winfo_height() or 480
                y = h - 30  # place icons slightly above the bottom edge
            else:
                y = 10
        except Exception:
            y = 10

        for i, app in enumerate(self.apps):
            label = getattr(app, "name", f"App{i}")[:8]
            if i == self.index:
                fg = "#99ff66" if not fb_active else self._feedback_color
            else:
                fg = "#66aa44"
            # Allow TkInterface to override tab fg (pulse effect)
            if hasattr(ctx, "_tab_fg_override") and ctx._tab_fg_override is not None and i == self.index:
                fg = ctx._tab_fg_override

            # Render optional icon if available on the rendering context
            icon_drawn = False
            try:
                full_key = getattr(app, "name", f"app{i}").lower()
                if hasattr(ctx, "icons") and full_key in ctx.icons and hasattr(ctx, "canvas"):
                    try:
                        ctx.canvas.create_image(x, y, image=ctx.icons[full_key], anchor="nw")
                        icon_drawn = True
                    except Exception:
                        # ignore icon drawing errors
                        icon_drawn = False
            except Exception:
                icon_drawn = False

            # Adjust text offset if icon drawn
            text_x = x + (24 if icon_drawn else 0)
            ctx.draw_text(text_x, y, label, fg=fg)
            x += 60
        # Delegate to active app
        if hasattr(self.current, "render"):
            self.current.render(ctx)
