class DummyApp:
    def __init__(self, name):
        self.name = name
    def render(self, ctx):
        # minimal render
        pass

class FakeCanvas:
    def __init__(self):
        self.images = []
        self.texts = []
    def create_image(self, x, y, image=None, anchor=None):
        self.images.append((x, y, getattr(image, 'name', str(image)), anchor))
    def create_text(self, *args, **kwargs):
        self.texts.append((args, kwargs))

class FakeCtx:
    def __init__(self):
        self.canvas = FakeCanvas()
        self.icons = {'placeholder': 'ICON_OBJ'}
        self._tab_fg_override = None
    def draw_text(self, x, y, text, fg=None):
        self.canvas.create_text((x, y), {'fg': fg, 'text': text})


def test_app_manager_renders_icons():
    from pipboy.interface.app_manager import AppManager

    apps = [DummyApp('placeholder'), DummyApp('Other')]
    am = AppManager(apps)
    ctx = FakeCtx()
    # call render and ensure icon draw occurred for first app
    am.render(ctx)
    assert len(ctx.canvas.images) >= 1
    assert any('placeholder' in str(i[2]) or i[2] == 'ICON_OBJ' for i in ctx.canvas.images)