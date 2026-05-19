"""Background-image steps: enhance, grain, resize."""

from __future__ import annotations

import logging

import numpy as np
from PIL import Image, ImageEnhance

try:
    LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    LANCZOS = Image.LANCZOS

log = logging.getLogger(__name__)


def enhance_image(image: Image.Image) -> Image.Image:
    """Subtle contrast + sharpness + saturation boost."""
    image = ImageEnhance.Contrast(image).enhance(1.08)
    image = ImageEnhance.Sharpness(image).enhance(1.10)
    image = ImageEnhance.Color(image).enhance(1.07)
    return image


def add_grain(
    image: Image.Image,
    intensity: float = 0.5,
    amount: float = 25,
    washout: float = 0.15,
    seed: int | None = None,
) -> Image.Image:
    """Add film grain. Seed makes it deterministic."""
    if intensity <= 0.0:
        return image
    rng = np.random.default_rng(seed)
    arr = np.array(image)
    scaled_amount = amount * intensity * 3
    scaled_washout = washout * intensity * 2
    noise = rng.normal(0, scaled_amount, arr.shape[:2])
    for c in range(3):
        arr[..., c] = arr[..., c] * (1 - scaled_washout) + (arr[..., c] + noise) * scaled_washout
    arr = np.clip(arr, 0, 255)
    return Image.fromarray(arr.astype(np.uint8), image.mode)


def resize_cover(image: Image.Image, canvas: tuple[int, int]) -> Image.Image:
    """Resize + center-crop so image fully covers the canvas."""
    cw, ch = canvas
    iw, ih = image.size
    scale = max(cw / iw, ch / ih)
    new_size = (int(iw * scale + 0.5), int(ih * scale + 0.5))
    resized = image.resize(new_size, LANCZOS)
    left = (resized.width - cw) // 2
    top = (resized.height - ch) // 2
    return resized.crop((left, top, left + cw, top + ch))
