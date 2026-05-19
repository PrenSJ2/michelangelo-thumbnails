"""IO helpers: fetch images from path/URL, hex parsing, font resolution."""

from __future__ import annotations

import logging
import pathlib
from io import BytesIO

import requests
from PIL import Image

log = logging.getLogger(__name__)

_ASSETS = pathlib.Path(__file__).resolve().parent.parent / 'assets'
_BUNDLED_FONTS = {
    'Herokid': _ASSETS / 'fonts' / 'Herokid' / 'Herokid-BoldCondensed.otf',
    'Herokid-Narrow': _ASSETS / 'fonts' / 'Herokid' / 'Herokid-BoldNarrow.otf',
}


def hex_to_rgb(color: str | tuple | None) -> tuple:
    """Convert a hex string or pass-through RGB tuple to an (r,g,b) tuple.

    Falls back to black on any invalid input.
    """
    if isinstance(color, tuple) and len(color) == 3:
        return color
    if isinstance(color, str):
        h = color.lstrip('#')
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        try:
            return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))
        except ValueError:
            log.warning('Invalid hex color: %r, using black', color)
            return (0, 0, 0)
    log.warning('Invalid color format: %r, using black', color)
    return (0, 0, 0)


def fetch_image(source: str, timeout: int = 30) -> Image.Image:
    """Fetch an image from an http(s) URL or local path."""
    if source.startswith(('http://', 'https://')):
        resp = requests.get(source, timeout=timeout)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content))
        img.load()
        return img
    path = pathlib.Path(source)
    if not path.exists():
        raise FileNotFoundError(f'Image not found: {source}')
    img = Image.open(path)
    img.load()
    return img


def resolve_font_path(font: str) -> str:
    """Resolve a font reference to an absolute path.

    Accepts: family name of a bundled font (e.g. "Herokid"), or a direct path.
    """
    if font in _BUNDLED_FONTS:
        return str(_BUNDLED_FONTS[font])
    candidate = pathlib.Path(font)
    if candidate.exists():
        return str(candidate)
    raise FileNotFoundError(f'Font not found: {font}')
