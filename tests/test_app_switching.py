from pipboy.app.file_manager import FileManagerApp
from pipboy.app.map import MapApp


def test_app_names():
    apps = [FileManagerApp(), MapApp()]
    assert [a.name for a in apps] == ["FileManager", "Map"]
