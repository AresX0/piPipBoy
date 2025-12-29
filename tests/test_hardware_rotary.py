def test_hardware_rotary_triggers_app_switching():
    from pipboy.interface.app_manager import AppManager
    from pipboy.app.file_manager import FileManagerApp
    from pipboy.app.map import MapApp
    from pipboy.interface.hardware_interface import HardwareInterface
    from pipboy.interface.gpio_input import KeyboardInput

    apps = [FileManagerApp(), MapApp()]
    am = AppManager(apps)
    disp = type("D", (), {"initialize": lambda s: None, "clear": lambda s: None, "update": lambda s: None, "draw_text": lambda *a, **k: None})()
    inp = KeyboardInput()

    hw = HardwareInterface(disp, inp, am)
    hw.initialize()

    # Handler should be registered
    assert "rot_right" in inp.handlers and "rot_left" in inp.handlers

    # Call handler directly
    inp.handlers["rot_right"]()
    assert am.current.name == "Map"

    # Simulate rotary left -> should go back to FileManager
    inp.handlers["rot_left"]()
    assert am.current.name == "FileManager"

    # Also verify KeyboardInput.simulate triggers the same handlers
    inp.simulate("rot_right")
    assert am.current.name == "Map"
