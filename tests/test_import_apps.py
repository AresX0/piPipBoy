def test_import_new_apps():
    from pipboy.app.fan import FanApp
    from pipboy.app.camera import CameraApp
    from pipboy.app.lights import LightsApp
    from pipboy.app.display import DisplayApp

    assert FanApp.name == 'Fan'
    assert CameraApp.name == 'Camera'
    assert LightsApp.name == 'Lights'
    assert DisplayApp.name == 'Display'
