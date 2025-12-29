from pipboy.app.map import MapApp


def test_map_recenter_on_back():
    m = MapApp()
    m.center = (10.0, 20.0)
    assert not m.recentered
    m.handle_input("back")
    assert m.center == (0.0, 0.0)
    assert m.recentered
