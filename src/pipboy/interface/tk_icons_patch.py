from __future__ import annotations

from pathlib import Path
from typing import Any


def attach_icon_support(ui: Any) -> None:
    """Attach simple icon-loading utilities to a Tk-based UI object.

    This function is intentionally non-invasive: it adds a `_load_icons` method
    and a property `app_manager` with a setter that triggers icon loading when
    the app list is assigned (tests set `tk.app_manager = AppManager(...)`).
    """
    # Avoid attaching multiple times
    if getattr(ui, "_icon_support_attached", False):
        return
    ui._icon_support_attached = True

    # Where to search for icons relative to the package
    # repo_icons should point to the repository root 'resources/icons'
    repo_icons = Path(__file__).parent.parent.parent.parent / "resources" / "icons"
    # src_icons is the package-local resources/icons
    src_icons = Path(__file__).parent.parent / "resources" / "icons"

    def _load_icons():
        try:
            from .icon_utils import find_or_create_icon
        except Exception:
            ui._icons = {}
            return
        ui._icons = {}
        apps = []
        if hasattr(ui, "app_manager") and getattr(ui, "app_manager") is not None:
            try:
                apps = [a.name for a in ui.app_manager.apps]
            except Exception:
                apps = []
        # Always ensure the common icons are present
        targets = sorted(set(apps + ["Camera", "FileManager", "Lights", "Fan", "Display", "exit", "clock", "debug", "radio", "settings"]))
        for name in targets:
            p = find_or_create_icon(name, [src_icons, repo_icons])
            if p is None:
                continue
            ui._icons[name] = str(p)
        # Print a small summary for logs
        try:
            print("Loaded icons:", {k: v for k, v in ui._icons.items()})
        except Exception:
            pass

    # Attach the loader
    ui._load_icons = _load_icons

    # Load icons immediately (defaults + app names if present)
    try:
        ui._load_icons()
    except Exception:
        pass

    # Add a property to intercept assignments to `app_manager`
    def _get_app_manager():
        return getattr(ui, "_app_manager_internal", None)

    def _set_app_manager(val):
        setattr(ui, "_app_manager_internal", val)
        # Trigger icon load on assignment
        try:
            ui._load_icons()
        except Exception:
            pass

    setattr(ui.__class__, "app_manager", property(_get_app_manager, _set_app_manager))
