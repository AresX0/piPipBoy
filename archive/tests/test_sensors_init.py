from pipboy.interface.tk_interface import TkInterface
from pipboy.driver.sensors.bme280 import BME280


def test_tkinterface_receives_sensors(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("theme: green\n")
    sensors = {"bme280": BME280()}
    tk = TkInterface(cfg, sensors=sensors)
    # The environment app in the manager should have the sensors dict
    env_app = [a for a in tk.app_manager.apps if getattr(a, "name", "") == "Environment"][0]
    assert getattr(env_app, "sensors", None) is sensors
