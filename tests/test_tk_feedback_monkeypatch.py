from pipboy.interface.tk_interface import TkInterface


def test_tkinterface_monkeypatch_load(monkeypatch, tmp_path):
    # Monkeypatch load_config to set custom theme values
    def fake_load(self):
        self.config = {"theme": "green", "themes": {"green": {"feedback_fg": "#ABCDEF", "feedback_duration": 3.0}}}

    monkeypatch.setattr(TkInterface, "load_config", fake_load)
    try:
        tk = TkInterface(tmp_path / "config.yaml")
    except Exception as e:
        import tkinter as _tk
        if isinstance(e, _tk.TclError):
            import pytest
            pytest.skip("no DISPLAY available; skipping TkInterface tests")
        raise
    am = tk.app_manager
    assert am._feedback_color == "#ABCDEF"
    assert am._feedback_duration == 3.0
