from pipboy.app.fan import FanApp
from pipboy.app.camera import CameraApp
from pipboy.app.lights import LightsApp
from pipboy.app.display import DisplayApp


class FakeController:
    def __init__(self):
        self.last = None

    def set_fan_speed(self, v):
        self.last = ('fan', v)
        return True

    def set_camera_enabled(self, ena):
        self.last = ('camera', ena)
        return True

    def set_led_pattern(self, pattern, color=None):
        self.last = ('led', pattern, color)
        return True


def test_fan_app_calls_controller():
    ctrl = FakeController()
    app = FanApp(controller=ctrl)
    res = app.handle_input({'set_fan': 42})
    assert res is True
    assert ctrl.last == ('fan', 42.0)


def test_camera_app_toggle_and_explicit():
    ctrl = FakeController()
    app = CameraApp(controller=ctrl)
    # toggle via select
    res = app.handle_input('select')
    assert res is True
    assert ctrl.last == ('camera', True)
    # explicit disable
    res = app.handle_input({'enable': False})
    assert res is True
    assert ctrl.last == ('camera', False)


def test_lights_app_pattern():
    ctrl = FakeController()
    app = LightsApp(controller=ctrl)
    res = app.handle_input({'pattern': 'solid', 'color': (10, 20, 30)})
    assert res is True
    assert ctrl.last == ('led', 'solid', (10, 20, 30))


def test_display_app_controls():
    app = DisplayApp()
    assert app.handle_input({'brightness': 50}) is True
    assert app.handle_input({'rotate': 90}) is True
    assert app.handle_input('select') == {'action': 'show_display_controls'}
