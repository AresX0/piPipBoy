class DummyApp:
    def __init__(self, name):
        self.name = name
        self.received = []
    def render(self, ctx):
        pass
    def handle_input(self, evt):
        self.received.append(evt)

class FakeRoot:
    def __init__(self):
        self.bindings = {}
        self._title = None
    def title(self, t):
        self._title = t
    def bind(self, name, func):
        self.bindings[name] = func
    def attributes(self, *a, **k):
        self._attrs = a
    def state(self, s):
        self._state = s

class FakeCanvas:
    def __init__(self, master=None, **kwargs):
        # accept width/height/bg kwargs like real Canvas
        self.master = master
        self.kwargs = kwargs
        self.rects = []
        self.images = []
    def create_rectangle(self, *a, **k):
        self.rects.append((a,k))
    def create_image(self, *a, **k):
        self.images.append((a,k))
    def create_text(self, *a, **k):
        pass
    def config(self, **k):
        pass
    def delete(self, *a, **k):
        pass
    def pack(self):
        pass

class Event:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def test_click_selects_tab(monkeypatch, tmp_path):
    from pipboy.interface.tk_interface import TkInterface
    from pipboy.interface.app_manager import AppManager

    # patch Tk and Canvas
    monkeypatch.setattr('tkinter.Tk', FakeRoot)
    monkeypatch.setattr('tkinter.Canvas', FakeCanvas)

    cfg = tmp_path / 'cfg.yaml'
    cfg.write_text('ui:\n  fullscreen: false\n  touch: true\n')

    apps = [DummyApp('A'), DummyApp('B'), DummyApp('C')]
    tk = TkInterface(cfg, sensors={}, fullscreen=None)
    tk.app_manager = AppManager(apps)

    # Click near the first tab (x ~ 15)
    e = Event(15, 10)
    tk._on_click(e)
    assert tk.app_manager.index == 0

    # Click near third tab (x ~ 10 + 2*60 + 5)
    e2 = Event(10 + 2*60 + 5, 10)
    tk._on_click(e2)
    assert tk.app_manager.index == 2


def test_swipe_changes_app(monkeypatch, tmp_path):
    from pipboy.interface.tk_interface import TkInterface
    from pipboy.interface.app_manager import AppManager

    monkeypatch.setattr('tkinter.Tk', FakeRoot)
    monkeypatch.setattr('tkinter.Canvas', FakeCanvas)

    cfg = tmp_path / 'cfg.yaml'
    cfg.write_text('ui:\n  touch: true\n')

    apps = [DummyApp('A'), DummyApp('B'), DummyApp('C')]
    tk = TkInterface(cfg, sensors={}, fullscreen=None)
    tk.app_manager = AppManager(apps)

    # Start in index 0
    tk.app_manager.index = 1
    tk._on_touch_start(Event(100, 50))
    # swipe left (dx negative) should go next
    tk._on_touch_end(Event(40, 50))
    assert tk.app_manager.index == 2

    # swipe right should go prev
    tk.app_manager.index = 1
    tk._on_touch_start(Event(40, 50))
    tk._on_touch_end(Event(120, 50))
    assert tk.app_manager.index == 0
