"""Segmentation dispatcher: rembg (local) / Pixian (paid HTTP) / none."""

from __future__ import annotations

import hashlib
import logging
import os
import pathlib
from io import BytesIO

from PIL import Image

log = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = pathlib.Path.home() / '.cache' / 'michelangelo-thumbnails' / 'masks'


def _rembg_available() -> bool:
    try:
        import rembg  # noqa: F401

        return True
    except ImportError:
        return False


def _white_mask(image: Image.Image) -> Image.Image:
    return Image.new('L', image.size, 255)


def _hash_image(image: Image.Image) -> str:
    buf = BytesIO()
    image.save(buf, format='PNG')
    return hashlib.sha256(buf.getvalue()).hexdigest()


def _cache_path(image: Image.Image, mode: str, cache_dir: pathlib.Path) -> pathlib.Path:
    return cache_dir / f'{_hash_image(image)}-{mode}.png'


def _load_cached(path: pathlib.Path) -> Image.Image | None:
    if path.exists():
        img = Image.open(path)
        img.load()
        return img.convert('L')
    return None


def _save_cached(mask: Image.Image, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mask.save(path)


def _segment_rembg(image: Image.Image) -> Image.Image:
    from rembg import remove

    out = remove(image)
    if out.mode != 'RGBA':
        out = out.convert('RGBA')
    return out.split()[-1]


def _segment_pixian(image: Image.Image) -> Image.Image:
    """Pixian client. Credentials from PIXIAN_API_KEY env (formatted "api_id:api_secret")."""
    import requests

    key = os.environ.get('PIXIAN_API_KEY')
    if not key:
        raise RuntimeError('PIXIAN_API_KEY env var not set')
    if ':' not in key:
        raise RuntimeError("PIXIAN_API_KEY must be 'api_id:api_secret'")
    api_id, api_secret = key.split(':', 1)

    buf = BytesIO()
    image.save(buf, format='PNG', optimize=True)
    files = {'image': ('image.png', buf.getvalue(), 'image/png')}
    resp = requests.post(
        'https://api.pixian.ai/api/v2/remove-background',
        files=files,
        data={'output.format': 'png'},
        auth=(api_id, api_secret),
        timeout=60,
    )
    resp.raise_for_status()
    out = Image.open(BytesIO(resp.content))
    out.load()
    if out.mode != 'RGBA':
        out = out.convert('RGBA')
    return out.split()[-1]


def segment(
    image: Image.Image,
    mode: str = 'auto',
    no_cache: bool = False,
    cache_dir: str | None = None,
) -> Image.Image:
    """Return an L-mode subject mask of `image`.

    Modes:
      auto    - pixian if PIXIAN_API_KEY set, else rembg if installed, else white.
      rembg   - force rembg; raise if not installed.
      pixian  - force pixian; raise if no key.
      none    - return all-white mask.
    """
    if mode == 'none':
        return _white_mask(image)

    cdir = pathlib.Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR

    if mode == 'auto':
        if os.environ.get('PIXIAN_API_KEY'):
            mode = 'pixian'
        elif _rembg_available():
            mode = 'rembg'
        else:
            log.warning(
                'Smart segmentation unavailable; install michelangelo-thumbnails[smart] '
                'or set PIXIAN_API_KEY. Falling back to none.'
            )
            return _white_mask(image)

    if not no_cache:
        path = _cache_path(image, mode, cdir)
        cached = _load_cached(path)
        if cached is not None:
            log.debug('Mask cache hit: %s', path)
            return cached

    if mode == 'rembg':
        if not _rembg_available():
            raise RuntimeError("rembg not installed. Run: pip install 'michelangelo-thumbnails[smart]'")
        mask = _segment_rembg(image)
    elif mode == 'pixian':
        mask = _segment_pixian(image)
    else:
        raise ValueError(f'Unknown segmenter mode: {mode!r}')

    if not no_cache:
        _save_cached(mask, _cache_path(image, mode, cdir))
    return mask
