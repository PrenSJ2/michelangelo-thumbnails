from PIL import Image, ImageDraw, ImageFont

from michelangelo_thumbnails.pipeline.io import resolve_font_path
from michelangelo_thumbnails.pipeline.text import (
    dominant_color,
    draw_additional_text,
    draw_title,
    wrap_text,
)


def _make_font(size=40):
    return ImageFont.truetype(resolve_font_path('Herokid'), size)


def test_wrap_text_short_one_line():
    font = _make_font()
    canvas = Image.new('RGB', (500, 100))
    draw = ImageDraw.Draw(canvas)
    lines = wrap_text('hi', font, max_width=500, draw=draw)
    assert lines == ['hi']


def test_wrap_text_breaks_long_text():
    font = _make_font()
    canvas = Image.new('RGB', (200, 200))
    draw = ImageDraw.Draw(canvas)
    lines = wrap_text('This text is definitely too wide', font, max_width=200, draw=draw)
    assert len(lines) >= 2


def test_dominant_color_red_image():
    src = Image.new('RGB', (50, 50), (255, 0, 0))
    r, g, b = dominant_color(src)
    assert r > 200 and g < 30 and b < 30


def test_draw_title_returns_image_same_size():
    base = Image.new('RGB', (1080, 1350), (200, 200, 200))
    out = draw_title(
        base,
        title='HELLO',
        font_path=resolve_font_path('Herokid'),
        font_size=80,
        color=(0, 0, 0),
        align='center',
        max_width=900,
    )
    assert out.size == base.size


def test_draw_additional_text_bottom():
    import numpy as np

    base = Image.new('RGB', (400, 600), (50, 50, 50))
    out = draw_additional_text(
        base,
        text='SUBTITLE',
        font_path=resolve_font_path('Herokid'),
        font_size=40,
        color=(255, 255, 255),
        align='center',
        position='bottom',
        bar_color=(0, 0, 0),
    )
    arr_in = np.array(base)
    arr_out = np.array(out)
    # bottom strip should differ (bar + text drawn there)
    assert not np.array_equal(arr_in[-100:], arr_out[-100:])
