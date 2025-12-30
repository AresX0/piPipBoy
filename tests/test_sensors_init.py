import pytest
pytest.importorskip("tkinter")
from pipboy.interface.tk_interface import TkInterface
from pipboy.driver.sensors.bme280 import BME280


def test_tkinterface_receives_sensors(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("theme: green\n")
    sensors = {"bme280": BME280()}
    try:
        tk = TkInterface(cfg, sensors=sensors)
    except Exception as e:
        # Tk may be present but not connected to a display; skip in that case
        import tkinter as _tk
        if isinstance(e, _tk.TclError):
            import pytest
            pytest.skip("no DISPLAY available; skipping TkInterface tests")
        raise
    # The environment app in the manager should have the sensors dict
    env_app = [a for a in tk.app_manager.apps if getattr(a, "name", "") == "Environment"][0]
    assert getattr(env_app, "sensors", None) is sensors
