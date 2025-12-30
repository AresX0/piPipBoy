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
        targets = sorted(set(apps + ["Camera", "FileManager", "Lights", "Fan", "Display", "exit", "clock", "debug",
            "radio", "settings"]))
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
            # Distribute icons into 2 or 3 rows, evenly spaced per row, fixed 12x12 icons
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
                # Fixed icon size requested
                size = 12
                padding = 8
                bottom_padding = 10
                row_spacing = size + 8

                # Prefer 2 rows unless too many icons; allow up to 3 rows
                rows = 2 if n <= 8 else 3

                # Distribute icons across rows as evenly as possible
                base = n // rows
                extra = n % rows
                counts = [(base + (1 if i < extra else 0)) for i in range(rows)]

                # If any row would have 0 items, reduce rows accordingly
                while rows > 1 and counts[-1] == 0:
                    rows -= 1
                    base = n // rows
                    extra = n % rows
                    counts = [(base + (1 if i < extra else 0)) for i in range(rows)]

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

                # Layout each row centered horizontally with even spacing
                index = 0
                y0 = height - bottom_padding
                for r in range(rows):
                    count = counts[r]
                    if count == 0:
                        continue
                    # gap between centers
                    gap = width / (count + 1)
                    # ensure minimal spacing
                    min_gap = size + padding
                    if gap < min_gap and rows < 3:
                        # try more rows to reduce crowding
                        rows = min(3, rows + 1)
                        base = n // rows
                        extra = n % rows
                        counts = [(base + (1 if i < extra else 0)) for i in range(rows)]
                        # restart layout
                        index = 0
                        y0 = height - bottom_padding
                        continue

                    # determine vertical position for this row (stack from bottom upwards)
                    y = int(y0 - r * row_spacing)
                    for c in range(count):
                        name = names[index]
                        index += 1
                        x = int((c + 1) * gap)
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
                            # log image size if possible for debugging layout
                            try:
                                iw = img.width() if hasattr(img, 'width') else None
                                ih = img.height() if hasattr(img, 'height') else None
                            except Exception:
                                iw = ih = None
                            try:
                                print(f"Placing icon '{name}' at ({x},{y}) img_size={iw}x{ih} target={size}")      
                            except Exception:
                                pass
                            item = canvas.create_image(x, y, image=img, anchor='s')
                            ui._icon_items.append(item)
                                try:
                                    # ensure icons are on top and log their actual bounding box
                                    canvas.tag_raise(item)
                                    bbox = canvas.bbox(item)
                                    print(f"Icon bbox for '{name}': {bbox}")
                                except Exception:
                                    pass
                                # Optional: draw visible debug markers when env var set so we can
                                # visually verify position/size on remote Pi screenshots
                                try:
                                    import os
                                    from pathlib import Path
                                    debug_on = os.environ.get('PIPBOY_ICON_DEBUG') or Path.home().joinpath('diagnostics','icon_debug_on').exists()
                                    if debug_on:
                                        try:
                                            # small rectangle above anchor point (anchor='s')
                                            r = canvas.create_rectangle(x - size//2, y - size, x + size//2, y, outline='red', width=1)
                                            t = canvas.create_text(x, y - size - 6, text=name[:1], fill='red')
                                            # keep debug items separate
                                            ui._icon_debug_items = getattr(ui, '_icon_debug_items', [])
                                            ui._icon_debug_items.extend([r, t])
                                            canvas.tag_raise(r)
                                            canvas.tag_raise(t)
                                        except Exception:
                                            pass
                                except Exception:
                                    pass

        # Schedule re-render attempts until icons are actually placed on canvas
        try:
            canvas = getattr(ui, 'canvas', None)
            if canvas is not None and hasattr(canvas.master, 'after'):
                # bind once to respond to resizes
                try:
                    if not getattr(ui, '_icon_bind_set', False):
                        try:
                            canvas.bind('<Configure>', lambda e: ui._render_icon_bar())
                        except Exception:
                            pass
                        ui._icon_bind_set = True
                except Exception:
                    pass

                def _attempt_render(attempts=[0]):
                    try:
                        ui._render_icon_bar()
                        attempts[0] += 1
                        # If items placed, print success and stop retrying
                        if getattr(ui, '_icon_items', None) and len(ui._icon_items) >= len(ui._icons):
                            try:
                                print(f"Icon render succeeded after {attempts[0]} attempts")
                            except Exception:
                                pass
                            # Try to capture the canvas contents to a local PNG for reliable debugging
                            try:
                                from pathlib import Path
                                diag = Path.home() / 'diagnostics'
                                diag.mkdir(parents=True, exist_ok=True)
                                ps_path = str(diag / 'pipboy_canvas.ps')
                                png_path = str(diag / 'pipboy_canvas_internal.png')
                                try:
                                    canvas.postscript(file=ps_path, colormode='color')
                                    # Try to convert via PIL (requires Ghostscript or ImageMagick fallback)        
                                    try:
                                        from PIL import Image
                                        img = Image.open(ps_path)
                                        img.save(png_path)
                                    except Exception:
                                        import subprocess
                                        try:
                                            subprocess.run(['convert', ps_path, png_path], check=True)
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                            except Exception:
                                pass
                            return
                        if attempts[0] < 20:
                            try:
                                canvas.master.after(250, _attempt_render)
                            except Exception:
                                pass
                    except Exception:
                        # schedule again in case layout wasn't ready
                        try:
                            if attempts[0] < 20:
                                canvas.master.after(250, _attempt_render)
                        except Exception:
                            pass
                try:
                    canvas.master.after(250, _attempt_render)
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
        am = getattr(inst, "_app_manager_internal", None)
        if am is None:
            # Lightweight proxy to avoid crashes before the real manager is assigned
            class _Proxy:
                apps = []
                def _is_feedback_active(self):
                    return False
                def __getattr__(self, name):
                    # Provide a callable that returns False for unknown methods
                    return lambda *a, **k: False
            return _Proxy()
        return am

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
