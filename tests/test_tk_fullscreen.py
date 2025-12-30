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

    monkeypatch.setattr('tkinter.Tk', FakeTk)
    from pipboy.interface.tk_interface import TkInterface

    cfg = tmp_path / "cfg.yaml"
    cfg.write_text('ui:\n  fullscreen: true\n')

    tk = TkInterface(cfg, sensors={}, fullscreen=None)
    # Since config requested fullscreen, FakeTk.attributes should have been set
    assert tk.root.attrs.get('-fullscreen') is True or tk.root._state == 'zoomed'