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

        # Prepare image cache and rendering helpers
        ui._tk_images = {}
        ui._icon_items = []
        ui.icon_size = getattr(ui, 'icon_size', 36)  # default compact size (px)

        def _get_tk_image(path: str, size: int):
            # Return a tkinter-compatible PhotoImage sized to (size, size)
            try:
                from PIL import Image, ImageTk
            except Exception:
                Image = None
                ImageTk = None
            try:
                if Image is not None:
                    img = Image.open(path).convert('RGBA')
                    img = img.resize((size, size), Image.LANCZOS)
                    tkimg = ImageTk.PhotoImage(img)
                else:
                    # fallback: use tkinter.PhotoImage and rely on subsample (approximate)
                    import tkinter as tk
                    tkimg = tk.PhotoImage(file=path)
                    # try integer subsample to make it reasonably small
                    try:
                        w = tkimg.width()
                        if w > size:
                            subs = max(1, int(round(w / size)))
                            tkimg = tkimg.subsample(subs, subs)
                    except Exception:
                        pass
                return tkimg
            except Exception:
                return None

        def _render_icon_bar():
            # Draw icons across the bottom in 2 or 3 compact rows (12x12 per request).
            try:
                canvas = getattr(ui, 'canvas', None)
                if canvas is None:
                    return
                # Resolve canvas size
                try:
                    width = int(canvas.kwargs.get('width', 800))
                except Exception:
                    try:
                        width = int(canvas.master.winfo_width())
                    except Exception:
                        width = 800
                try:
                    height = int(canvas.kwargs.get('height', 600))
                except Exception:
                    try:
                        height = int(canvas.master.winfo_height())
                    except Exception:
                        height = 600
                names = list(ui._icons.keys())
                if not names:
                    return

                n = len(names)
                # Desired fixed icon size
                size = 12
                padding = 6  # horizontal padding between icon and slot
                bottom_padding = 8
                row_spacing = size + 8

                # Choose number of rows (prefer 2, but use 3 for many icons)
                rows = 2 if n <= 8 else 3
                # make sure icons will fit horizontally, else increase rows up to 3
                from math import ceil
                while rows <= 3:
                    cols = ceil(n / rows)
                    # compute gap between icon centers available
                    total_space = max(0, width - 20)
                    gap = total_space / (cols + 1)
                    if gap >= (size + padding) or rows == 3:
                        break
                    rows += 1

                cols = ceil(n / rows)
                gap = max(1, int((max(0, width - 20)) / (cols + 1)))

                # Clear previous icon items
                try:
                    for item in getattr(ui, '_icon_items', []):
                        try:
                            canvas.delete(item)
                        except Exception:
                            pass
                except Exception:
                    pass
                ui._icon_items = []

                ui._tk_images = ui._tk_images or {}

                # If available, bind canvas resize to re-render bar
                try:
                    if hasattr(canvas.master, 'bind'):
                        def _re(e):
                            try:
                                ui._render_icon_bar()
                            except Exception:
                                pass
                        canvas.master.bind('<Configure>', _re)
                except Exception:
                    pass

                # Layout icons into rows/cols
                left_margin = 10
                for idx, name in enumerate(names):
                    row = idx // cols
                    col = idx % cols
                    x = int(left_margin + (col + 1) * gap)
                    y = int(height - bottom_padding - row * row_spacing)
                    path = ui._icons.get(name)
                    if path is None:
                        continue
                    key = (path, size)
                    img = ui._tk_images.get(key)
                    if img is None:
                        img = _get_tk_image(path, size)
                        if img is None:
                            continue
                        ui._tk_images[key] = img
                    try:
                        item = canvas.create_image(x, y, image=img, anchor='s')
                        ui._icon_items.append(item)
                    except Exception:
                        pass
            except Exception:
                pass

        ui._render_icon_bar = _render_icon_bar

        # If we have access to a Tk 'after', schedule a delayed re-render to catch
        # layout finalization (canvas size might not be set at attach time).
        try:
            canvas = getattr(ui, 'canvas', None)
            if canvas is not None and hasattr(canvas.master, 'after'):
                try:
                    canvas.master.after(500, ui._render_icon_bar)
                except Exception:
                    pass
        except Exception:
            pass

        # Print a small summary for logs
        try:
            print("Loaded icons:", {k: v for k, v in ui._icons.items()})
        except Exception:
            pass

    # Attach the loader
    ui._load_icons = _load_icons

    # If the instance already set app_manager in its constructor, move it into
    # our internal storage so the property behaves the same as before.
    try:
        if 'app_manager' in ui.__dict__:
            try:
                ui._app_manager_internal = ui.__dict__.pop('app_manager')
            except Exception:
                pass
    except Exception:
        pass

    # Load icons immediately (defaults + app names if present) and render the bar
    try:
        ui._load_icons()
        try:
            ui._render_icon_bar()
        except Exception:
            pass
    except Exception:
        pass

    # Add a property to intercept assignments to `app_manager`
    def _get_app_manager(inst):
        return getattr(inst, "_app_manager_internal", None)

    def _set_app_manager(inst, val):
        setattr(inst, "_app_manager_internal", val)
        # Trigger icon load on assignment
        try:
            inst._load_icons()
        except Exception:
            pass
        # Also render icon bar if possible
        try:
            inst._render_icon_bar()
        except Exception:
            pass

    setattr(ui.__class__, "app_manager", property(_get_app_manager, _set_app_manager))
