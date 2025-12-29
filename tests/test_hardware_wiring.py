class DummyDisplay:
    def __init__(self):
        self.ops = []
        self.inited = False

    def initialize(self):
        self.inited = True

    def clear(self):
        self.ops.append(("clear",))

    def draw_text(self, x, y, text, color=None):
        self.ops.append(("text", x, y, text, color))

    def update(self):
        self.ops.append(("update",))


class DummyInputs:
    def __init__(self):
        self.handlers = {}

    def on(self, name, handler):
        self.handlers[name] = handler


def test_hardware_interface_wires_inputs_and_renders():
    from pipboy.interface.app_manager import AppManager
    from pipboy.app.file_manager import FileManagerApp
    from pipboy.app.map import MapApp
    from pipboy.interface.hardware_interface import HardwareInterface

    apps = [FileManagerApp(), MapApp()]
    am = AppManager(apps)
    disp = DummyDisplay()
    inp = DummyInputs()

    hw = HardwareInterface(disp, inp, am)
    hw.initialize()

    # input handlers should be wired
    assert "next" in inp.handlers and "prev" in inp.handlers and "select" in inp.handlers

    # render once
    hw.run_once()
    # operations include clear, text and update
    assert any(op[0] == "clear" for op in disp.ops)
    assert any(op[0] == "update" for op in disp.ops)
    # simulate input
    inp.handlers["next"]()
    hw.run_once()
    # now current app should be Map (second app)
    assert am.current.name == "Map"
