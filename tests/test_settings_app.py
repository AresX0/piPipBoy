from pipboy.app.settings import SettingsApp

class DummyController:
    def __init__(self):
        self.fan = None
        self.camera = None
        self.led = None
    def set_fan_speed(self, v):
        self.fan = v
        return True
    def set_camera_enabled(self, v):
        self.camera = v
        return True
    def set_led_pattern(self, pattern, color=None):
        self.led = (pattern, color)
        return True


def test_settings_handles_inputs():
    ctrl = DummyController()
    app = SettingsApp(controller=ctrl)

    app.handle_input({"type": "set_fan", "value": 42})
    assert ctrl.fan == 42
    assert "set_fan" in app._last_status

    app.handle_input({"type": "set_camera", "value": True})
    assert ctrl.camera is True
    assert "set_camera" in app._last_status

    app.handle_input({"type": "set_led", "pattern": "solid", "color": "#010203"})
    assert ctrl.led[0] == "solid"
    assert ctrl.led[1] == (1,2,3)
    assert "set_led" in app._last_status