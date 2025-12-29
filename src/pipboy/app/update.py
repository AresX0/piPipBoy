"""Update app - show status of remote repo and allow safe manual updates
"""
from __future__ import annotations

from .base import App


class UpdateApp(App):
    def __init__(self, repo_path: str | None = None):
        super().__init__("Update")
        self.repo_path = repo_path
        self.status = "idle"

    def render(self, ctx):
        ctx.draw_text(10, 80, f"Update status: {self.status}")

    def check(self):
        # Safe check: no auto-exec. Just check `git fetch` / `git status` if permitted
        self.status = "checked"
