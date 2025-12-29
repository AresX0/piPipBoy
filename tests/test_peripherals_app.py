from pipboy.app.peripherals_app import PeripheralsApp


class DummyPeripheral:
    def __init__(self):
        self.speed = 0

    def set_speed(self, v):
        self.speed = v


class DummyLED:
    def __init__(self):
        self.brightness = 100

    def set_brightness(self, b):
        self.brightness = b


class DummyOLED:
    def __init__(self):
        self.lines = []

    def display_text(self, *lines):
        self.lines = list(lines)

    def clear(self):
        self.lines = []


class DummyCam:
    def capture_image(self):
        return b"ok"


class DummyAppManager:
    def __init__(self):
        self.peripherals = {"fan": DummyPeripheral(), "leds": DummyLED(), "oled": DummyOLED(), "camera": DummyCam()}


def test_peripherals_app_actions():
    app = PeripheralsApp()
    app.app_manager = DummyAppManager()

    app.handle_input('up')
    assert app._fan_target == 10
    assert app.app_manager.peripherals['fan'].speed == 10

    app.handle_input('right')
    assert app._led_brightness == 100
    app.handle_input('down')
    assert app._fan_target == 0
    app.handle_input('rot_right')
    assert app._oled_lines[0].startswith('T:')
    app.handle_input('select')
    assert app._camera_status == 'idle'
