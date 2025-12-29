from pipboy.interface.tk_interface import _blend_hex


def test_blend_hex_midpoint():
    # blend black and white halfway -> mid-gray
    assert _blend_hex("#000000", "#ffffff", 0.5) in ("#7f7f7f", "#808080")


def test_blend_hex_extremes():
    assert _blend_hex("#112233", "#112233", 0.0) == "#112233"
    assert _blend_hex("#112233", "#112233", 1.0) == "#112233"
