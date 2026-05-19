import numpy as np
from PIL import Image

from michelangelo_thumbnails.pipeline.background import (
    add_grain,
    enhance_image,
    resize_cover,
)


def _solid(size, color):
    return Image.new('RGB', size, color)


def test_resize_cover_matches_canvas():
    src = _solid((2000, 1000), (128, 128, 128))
    out = resize_cover(src, (1080, 1350))
    assert out.size == (1080, 1350)


def test_resize_cover_taller_than_canvas():
    src = _solid((500, 5000), (128, 128, 128))
    out = resize_cover(src, (1080, 1350))
    assert out.size == (1080, 1350)


def test_enhance_image_changes_pixels():
    # Use a non-grey color: contrast/color enhancers are no-ops on uniform grey
    src = _solid((100, 100), (100, 80, 60))
    out = enhance_image(src)
    arr_in = np.array(src)
    arr_out = np.array(out)
    assert not np.array_equal(arr_in, arr_out)


def test_add_grain_zero_intensity_is_noop():
    src = _solid((50, 50), (128, 128, 128))
    out = add_grain(src, intensity=0.0)
    assert np.array_equal(np.array(src), np.array(out))


def test_add_grain_with_seed_is_deterministic():
    src = _solid((50, 50), (128, 128, 128))
    a = add_grain(src.copy(), intensity=0.5, seed=42)
    b = add_grain(src.copy(), intensity=0.5, seed=42)
    assert np.array_equal(np.array(a), np.array(b))


def test_add_grain_different_seed_differs():
    src = _solid((50, 50), (128, 128, 128))
    a = add_grain(src.copy(), intensity=0.5, seed=1)
    b = add_grain(src.copy(), intensity=0.5, seed=2)
    assert not np.array_equal(np.array(a), np.array(b))
