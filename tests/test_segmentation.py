import pytest
from PIL import Image

from michelangelo_thumbnails.pipeline.segmentation import segment


def test_segment_none_mode_returns_white_mask():
    img = Image.new('RGB', (64, 64), (128, 128, 128))
    mask = segment(img, mode='none')
    assert mask.mode == 'L'
    assert mask.size == (64, 64)
    assert mask.getpixel((0, 0)) == 255
    assert mask.getpixel((32, 32)) == 255


def test_segment_auto_falls_back_to_none_when_no_backend(monkeypatch):
    monkeypatch.delenv('PIXIAN_API_KEY', raising=False)
    monkeypatch.setattr(
        'michelangelo_thumbnails.pipeline.segmentation._rembg_available',
        lambda: False,
    )
    img = Image.new('RGB', (64, 64), (128, 128, 128))
    mask = segment(img, mode='auto')
    assert mask.getpixel((0, 0)) == 255


def test_segment_rembg_raises_when_not_installed(monkeypatch):
    monkeypatch.setattr(
        'michelangelo_thumbnails.pipeline.segmentation._rembg_available',
        lambda: False,
    )
    img = Image.new('RGB', (64, 64), (128, 128, 128))
    with pytest.raises(RuntimeError, match='rembg'):
        segment(img, mode='rembg')


def test_segment_pixian_raises_without_key(monkeypatch):
    monkeypatch.delenv('PIXIAN_API_KEY', raising=False)
    img = Image.new('RGB', (64, 64), (128, 128, 128))
    with pytest.raises(RuntimeError, match='PIXIAN_API_KEY'):
        segment(img, mode='pixian')
