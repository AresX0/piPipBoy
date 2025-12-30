from pathlib import Path
import tempfile
from pipboy.interface.icon_utils import find_or_create_icon


def test_find_or_create_icon_creates(tmp_path):
    d = tmp_path / 'icons'
    d.mkdir()
    p = find_or_create_icon('Camera', [d])
    assert p is not None
    assert p.exists()
    assert p.name == 'camera.png'


def test_find_or_create_icon_finds_existing(tmp_path):
    d = tmp_path / 'icons'
    d.mkdir()
    # create a file with mixed-case
    f = d / 'Camera.png'
    f.write_bytes(b'fake')
    p = find_or_create_icon('Camera', [d])
    assert p == f
