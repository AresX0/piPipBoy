from pipboy.driver.peripherals import FanController, LEDController, OLEDController, CameraInterface


def test_fan_controller_basic():
    f = FanController()
    assert f.get_speed() == 0
    f.set_speed(50)
    assert f.get_speed() == 50
    f.set_speed(200)
    assert f.get_speed() == 100


def test_led_controller_basic():
    l = LEDController()
    l.set_color((10, 20, 30))
    l.set_brightness(42)
    assert l.get_state()[1] == 42


def test_oled_controller_basic():
    o = OLEDController()
    o.display_text("Line1", "Line2")
    assert o.get_lines() == ["Line1", "Line2"]
    o.clear()
    assert o.get_lines() == []


def test_camera_interface_stub(tmp_path):
    c = CameraInterface()
    data = c.capture_image(path=str(tmp_path / "x.bin"))
    assert data is not None
    assert (tmp_path / "x.bin").exists()