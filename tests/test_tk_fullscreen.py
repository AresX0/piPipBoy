import pytest
import types


def test_tkinterface_sets_fullscreen(monkeypatch, tmp_path):
    # Create a fake Tk with attributes/state tracking
    class FakeTk:
        def __init__(self):
            self.attrs = {}
            self._state = None
        def title(self, t):
            self._title = t
        def attributes(self, name, value=None):
            self.attrs[name] = value
        def state(self, s):
            self._state = s
        def bind(self, *a, **k):
            pass
        def after(self, *a, **k):
            pass
        def mainloop(self):
            pass

    class FakeCanvas:
        def __init__(self, master=None, **kwargs):
            self.master = master
        def pack(self):
            pass
        def create_text(self, *a, **k):
            pass
        def config(self, **k):
            pass
        def delete(self, *a, **k):
            pass

    monkeypatch.setattr('tkinter.Tk', FakeTk)
    monkeypatch.setattr('tkinter.Canvas', FakeCanvas)
    from pipboy.interface.tk_interface import TkInterface

    cfg = tmp_path / "cfg.yaml"
    cfg.write_text('ui:\n  fullscreen: true\n')

    tk = TkInterface(cfg, sensors={}, fullscreen=None)
    # Since config requested fullscreen, FakeTk.attributes should have been set
    assert tk.root.attrs.get('-fullscreen') is True or tk.root._state == 'zoomed'