class FakeSPI:
    def __init__(self):
        self.available = True
        self.sent = []

    def xfer2(self, b: bytes):
        self.sent.append(bytes(b))
        return b


def _concat_sent(spi):
    return b"".join(spi.sent)


def test_initialization_sequence():
    from pipboy.interface.ili9486_driver import ILI9486

    spi = FakeSPI()
    d = ILI9486(spi)
    d.initialize()
    data = _concat_sent(spi)
    # Should contain SWRESET (0x01), SLPOUT (0x11), COLMOD (0x3A), MADCTL (0x36), DISPON (0x29)
    assert b"\x01" in data and b"\x11" in data and b"\x3A" in data and b"\x36" in data and b"\x29" in data


def test_set_window_and_fill_rect():
    from pipboy.interface.ili9486_driver import ILI9486

    spi = FakeSPI()
    d = ILI9486(spi)
    # set window
    d.set_window(0, 0, 1, 1)
    data = _concat_sent(spi)
    # CASET and RASET commands (0x2A, 0x2B)
    assert b"\x2A" in data and b"\x2B" in data

    spi.sent.clear()
    d.fill_rect(0, 0, 2, 2, 0xF800)  # solid red
    data = _concat_sent(spi)
    # Should contain RAMWR command and pixel bytes for 4 pixels
    assert b"\x2C" in data
    # Pixel bytes include 0xF8 (first byte of 0xF800)
    assert b"\xF8" in data
