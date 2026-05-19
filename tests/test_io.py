import pathlib

import pytest
from PIL import Image

from michelangelo_thumbnails.pipeline.io import (
    fetch_image,
    hex_to_rgb,
    resolve_font_path,
)

FIXTURES = pathlib.Path(__file__).parent / 'fixtures'


def test_hex_to_rgb_with_hash():
    assert hex_to_rgb('#FF0000') == (255, 0, 0)


def test_hex_to_rgb_without_hash():
    assert hex_to_rgb('00ff00') == (0, 255, 0)


def test_hex_to_rgb_short_form():
    assert hex_to_rgb('#f00') == (255, 0, 0)


def test_hex_to_rgb_passthrough_tuple():
    assert hex_to_rgb((1, 2, 3)) == (1, 2, 3)


def test_hex_to_rgb_invalid_falls_back_to_black():
    assert hex_to_rgb(None) == (0, 0, 0)


def test_fetch_image_from_local_path():
    img = fetch_image(str(FIXTURES / 'red64.png'))
    assert isinstance(img, Image.Image)
    assert img.size == (64, 64)


def test_fetch_image_missing_path_raises():
    with pytest.raises(FileNotFoundError):
        fetch_image(str(FIXTURES / 'missing.png'))


def test_resolve_font_path_bundled_herokid():
    p = resolve_font_path('Herokid')
    assert p.endswith('.otf')
    assert pathlib.Path(p).exists()


def test_resolve_font_path_custom_path():
    custom = str(FIXTURES / 'red64.png')  # any existing file
    assert resolve_font_path(custom) == custom


def test_resolve_font_path_unknown_raises():
    with pytest.raises(FileNotFoundError):
        resolve_font_path('NonexistentFontFamily')
