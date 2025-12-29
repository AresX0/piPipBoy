from pipboy.interface.app_manager import AppManager
from pipboy.app.file_manager import FileManagerApp
from pipboy.app.map import MapApp


class DummyCtx:
    def __init__(self):
        self.drawn = []

    def draw_text(self, x, y, text, fg=None):
        self.drawn.append((x, y, text, fg))


def test_app_manager_switching():
    a = AppManager([FileManagerApp(), MapApp()])
    ctx = DummyCtx()
    a.render(ctx)
    # tabs drawn + app rendered (FileManager name should be visible in its render call)
    assert any("FileManager" in t[2] for t in ctx.drawn)

    a.handle_input("next")
    ctx2 = DummyCtx()
    a.render(ctx2)
    assert any("Map" in t[2] for t in ctx2.drawn)


def test_app_manager_prev_wrap():
    a = AppManager([FileManagerApp(), MapApp()])
    a.prev()
    assert a.current.name == "Map"
