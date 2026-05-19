"""Title, additional text, and dominant-color extraction."""

from __future__ import annotations

import logging
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger(__name__)


def wrap_text(
    text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw
) -> list[str]:
    """Greedy word-wrap to fit max_width."""
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        test_line = ' '.join([*current, word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(' '.join(current))
                current = [word]
            else:
                lines.append(word)
                current = []
    if current:
        lines.append(' '.join(current))
    return lines


def dominant_color(image: Image.Image, ignore_alpha: bool = True) -> tuple[int, int, int]:
    """Return the most common non-transparent pixel color, quantized to 16-step buckets."""
    img = image.convert('RGBA').resize((50, 50))
    pixels = [
        (r // 16 * 16, g // 16 * 16, b // 16 * 16)
        for (r, g, b, a) in img.get_flattened_data()
        if not (ignore_alpha and a < 128)
    ]
    if not pixels:
        return (0, 0, 0)
    return Counter(pixels).most_common(1)[0][0]


def draw_title(
    base: Image.Image,
    title: str,
    font_path: str,
    font_size: int,
    color: tuple[int, int, int],
    align: str = 'center',
    max_width: int | None = None,
    bottom_margin: int | None = None,  # default 8% of canvas height
    bottom_reserve: int = 0,  # additional pixels reserved at bottom (e.g. footer bar)
) -> Image.Image:
    """Draw a wrapped title onto a copy of `base`."""
    canvas = base.copy()
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(font_path, font_size)
    max_width = max_width or int(canvas.width * 0.9)
    lines = wrap_text(title, font, max_width, draw)

    line_height = int(font_size * 1.15)
    total_h = line_height * len(lines)

    if bottom_margin is None:
        bottom_margin = int(canvas.height * 0.08)
    bottom_edge = canvas.height - bottom_margin - bottom_reserve
    y = bottom_edge - total_h

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        if align == 'left':
            x = int(canvas.width * 0.05)
        elif align == 'right':
            x = canvas.width - line_w - int(canvas.width * 0.05)
        else:
            x = (canvas.width - line_w) // 2
        draw.text((x, y), line, font=font, fill=color)
        y += line_height
    return canvas


def draw_additional_text(
    base: Image.Image,
    text: str,
    font_path: str,
    font_size: int,
    color: tuple[int, int, int],
    align: str,
    position: str,
    bar_color: tuple[int, int, int] | None,
) -> Image.Image:
    """Draw additional text with an optional background bar and gradient fade.

    position: 'top', 'above_title', or 'bottom'.

    Reference port from preview_generator.py lines ~1700-1755:
      - For position='bottom': solid bar at bottom (120 + text_height), gradient fade 200px above.
      - For position='top': mirror to top (bar + gradient fade pointing down).
      - For position='above_title': just draw the text band centered around y ~70% of canvas height.
    """
    canvas = base.convert('RGBA').copy()
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(font_path, font_size)
    w, h = canvas.size

    max_text_w = int(w * 0.9)
    lines = wrap_text(text, font, max_text_w, draw)
    line_height = int(font_size * 1.2)
    text_block_h = line_height * len(lines)

    if position == 'bottom':
        bar_h = 120 + text_block_h
        if bar_color is not None:
            bar = Image.new('RGBA', (w, bar_h), (*bar_color, 255))
            canvas.alpha_composite(bar, (0, h - bar_h))
            # gradient fade above
            fade_h = 200
            gradient = Image.new('L', (1, fade_h))
            for y in range(fade_h):
                gradient.putpixel((0, y), int(255 * (y / fade_h)))
            alpha = gradient.resize((w, fade_h))
            fade = Image.new('RGBA', (w, fade_h), (*bar_color, 255))
            fade.putalpha(alpha)
            canvas.alpha_composite(fade, (0, h - bar_h - fade_h))
        text_y = h - bar_h + (bar_h - text_block_h) // 2
    elif position == 'top':
        bar_h = 120 + text_block_h
        if bar_color is not None:
            bar = Image.new('RGBA', (w, bar_h), (*bar_color, 255))
            canvas.alpha_composite(bar, (0, 0))
            fade_h = 200
            gradient = Image.new('L', (1, fade_h))
            for y in range(fade_h):
                gradient.putpixel((0, y), int(255 * (1 - y / fade_h)))
            alpha = gradient.resize((w, fade_h))
            fade = Image.new('RGBA', (w, fade_h), (*bar_color, 255))
            fade.putalpha(alpha)
            canvas.alpha_composite(fade, (0, bar_h))
        text_y = (bar_h - text_block_h) // 2
    else:  # above_title
        text_y = int(h * 0.7) - text_block_h // 2

    draw = ImageDraw.Draw(canvas)
    y = text_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        if align == 'left':
            x = int(w * 0.05)
        elif align == 'right':
            x = w - line_w - int(w * 0.05)
        else:
            x = (w - line_w) // 2
        draw.text((x, y), line, font=font, fill=color)
        y += line_height

    return canvas.convert(base.mode)
