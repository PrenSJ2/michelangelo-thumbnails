import numpy as np
from PIL import Image

from michelangelo_thumbnails.pipeline.circles import (
    blob_crop_with_border,
    circular_crop_with_border,
    create_text_circle,
    place_circle,
)


def test_create_text_circle_dimensions():
    out = create_text_circle('HOT', diameter=200, color=(255, 0, 0))
    assert out.size == (200, 200)
    assert out.mode == 'RGBA'


def test_circular_crop_no_border_dimensions():
    src = Image.new('RGB', (300, 300), (128, 128, 128))
    out = circular_crop_with_border(src, diameter=200, border=0, border_color=(255, 255, 255))
    assert out.size == (200, 200)
    # corners should be transparent
    assert out.getpixel((0, 0))[3] == 0
    # center should be opaque
    assert out.getpixel((100, 100))[3] == 255


def test_circular_crop_with_border_grows_canvas():
    src = Image.new('RGB', (300, 300), (128, 128, 128))
    out = circular_crop_with_border(src, diameter=200, border=10, border_color=(255, 255, 255))
    assert out.size == (220, 220)


def test_blob_crop_returns_rgba():
    src = Image.new('RGB', (200, 200), (128, 128, 128))
    out = blob_crop_with_border(src, diameter=200, border=0, border_color=(255, 255, 255))
    assert out.mode == 'RGBA'
    assert out.size == (200, 200)


def test_place_circle_fallback_corner_top_right():
    canvas = (1080, 1350)
    pos = place_circle(canvas=canvas, diameter=400, mask=None, corner='top-right', margin=80, avoid=[])
    # top-right corner placement
    assert pos[0] + 400 + 80 == 1080  # right edge - margin
    assert pos[1] == 80  # top + margin


def test_place_circle_smart_uses_mask():
    canvas = (1080, 1350)
    # subject mask: left half opaque, right half transparent
    mask = Image.new('L', canvas, 0)
    arr = np.array(mask)
    arr[:, :540] = 255
    mask = Image.fromarray(arr, 'L')
    pos = place_circle(canvas, 400, mask, 'top-right', 80, [])
    # smart placement should prefer right (transparent) side
    cx = pos[0] + 200
    assert cx > 540, f'expected circle right of subject, got cx={cx}'
