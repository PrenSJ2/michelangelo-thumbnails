"""Nightly-only: exercises real rembg model download (~170MB)."""

import pytest
from PIL import Image

rembg = pytest.importorskip('rembg')

from michelangelo_thumbnails.pipeline.segmentation import segment  # noqa: E402


def test_rembg_produces_mask_with_subject():
    import numpy as np

    arr = np.full((200, 200, 3), 255, dtype=np.uint8)
    yy, xx = np.ogrid[:200, :200]
    disc = (xx - 100) ** 2 + (yy - 100) ** 2 <= 60**2
    arr[disc] = [255, 0, 0]
    img = Image.fromarray(arr, 'RGB')
    mask = segment(img, mode='rembg', no_cache=True)
    assert mask.mode == 'L'
    assert mask.getpixel((100, 100)) > 100
