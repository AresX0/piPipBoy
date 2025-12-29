from pipboy.interface.app_manager import AppManager


class DummyApp:
    def __init__(self, name):
        self.name = name

    def render(self, ctx):
        ctx.draw_text(0, 0, f"{self.name}")


class DummyCtx:
    def __init__(self):
        self.drawn = []

    def draw_text(self, x, y, text, fg=None):
        self.drawn.append((x, y, text, fg))


def test_feedback_color_and_duration():
    a1 = DummyApp("A1")
    a2 = DummyApp("A2")
    am = AppManager([a1, a2], feedback_color="#abc123", feedback_duration=10.0)
    am.next()  # trigger feedback
    ctx = DummyCtx()
    am.render(ctx)
    # find selected tab entry (A2) and check its color equals feedback_color while feedback active
    sel_entries = [e for e in ctx.drawn if isinstance(e[2], str) and "A2" in e[2]]
    assert sel_entries, "Selected tab label missing"
    assert sel_entries[0][3] == "#abc123"
