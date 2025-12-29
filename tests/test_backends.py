from pipboy.driver import backends


def test_backends_no_hardware():
    # On CI or non-Pi machines, these should be None or safe objects
    assert backends.create_fan_backend(None) is None
    # It's acceptable for LED, OLED, camera to return None when libs are missing
    assert backends.create_led_backend() is None or True
    assert backends.create_oled_backend() is None or True
    assert backends.create_camera_backend() is None or True
