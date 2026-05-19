import numpy as np
from PIL import Image

from michelangelo_thumbnails.pipeline.logo import draw_logo


def test_draw_logo_changes_pixels():
    base = Image.new('RGB', (400, 600), (128, 128, 128))
    logo = Image.new('RGBA', (200, 80), (255, 0, 0, 255))
    out = draw_logo(
        base,
        logo,
        position='bottom',
        align='center',
        max_width=200,
        max_height=80,
        show_lines=False,
        line_color=(255, 255, 255),
        line_style='solid',
        line_thickness=2,
        line_margin=20,
        line_length=100,
    )
    assert not np.array_equal(np.array(base), np.array(out))


def test_draw_logo_with_solid_lines():
    base = Image.new('RGB', (400, 600), (128, 128, 128))
    logo = Image.new('RGBA', (200, 80), (255, 0, 0, 255))
    out = draw_logo(
        base,
        logo,
        position='bottom',
        align='center',
        max_width=200,
        max_height=80,
        show_lines=True,
        line_color=(255, 255, 255),
        line_style='solid',
        line_thickness=2,
        line_margin=20,
        line_length=100,
    )
    assert not np.array_equal(np.array(base), np.array(out))


def test_draw_logo_dashed_lines():
    base = Image.new('RGB', (400, 600), (128, 128, 128))
    logo = Image.new('RGBA', (100, 40), (255, 255, 0, 255))
    out = draw_logo(
        base,
        logo,
        position='top',
        align='center',
        max_width=100,
        max_height=40,
        show_lines=True,
        line_color=(255, 255, 255),
        line_style='dashed',
        line_thickness=2,
        line_margin=10,
        line_length=60,
    )
    # output should differ near the top (logo + lines)
    arr_in = np.array(base)
    arr_out = np.array(out)
    assert not np.array_equal(arr_in[:80], arr_out[:80])


def test_draw_logo_fade_lines():
    base = Image.new('RGB', (400, 600), (128, 128, 128))
    logo = Image.new('RGBA', (100, 40), (255, 255, 0, 255))
    out = draw_logo(
        base,
        logo,
        position='bottom',
        align='center',
        max_width=100,
        max_height=40,
        show_lines=True,
        line_color=(255, 255, 255),
        line_style='fade',
        line_thickness=2,
        line_margin=10,
        line_length=60,
    )
    # fade style must not crash and must change pixels
    assert not np.array_equal(np.array(base), np.array(out))
