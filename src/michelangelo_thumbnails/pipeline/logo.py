"""Logo overlay with optional decorative flanking lines."""

from __future__ import annotations

import logging

from PIL import Image, ImageDraw

try:
    LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    LANCZOS = Image.LANCZOS

log = logging.getLogger(__name__)


def _resize_logo(logo: Image.Image, max_w: int, max_h: int) -> Image.Image:
    """Resize preserving aspect ratio to fit within max_w x max_h."""
    w, h = logo.size
    if w <= max_w and h <= max_h:
        return logo
    scale = min(max_w / w, max_h / h)
    return logo.resize((int(w * scale), int(h * scale)), LANCZOS)


def _resolve_position(
    canvas_w: int, canvas_h: int, logo_w: int, logo_h: int, position: str, align: str
) -> tuple[int, int]:
    edge_margin = 80  # padding from left/right/bottom edges
    top_margin = 20  # tighter padding from top edge
    if align == 'left':
        x = edge_margin
    elif align == 'right':
        x = canvas_w - logo_w - edge_margin
    else:
        x = (canvas_w - logo_w) // 2

    if position == 'top':
        y = top_margin
    elif position == 'above_title':
        y = int(canvas_h * 0.65)  # rough above-title slot
    else:  # 'bottom'
        y = canvas_h - logo_h - edge_margin
    return x, y


def _draw_solid_line(draw, x1, y1, x2, y2, color):
    draw.rectangle([x1, y1, x2, y2], fill=color)


def _draw_dashed_line(draw, x1, y1, x2, y2, color, dash=8, gap=4):
    cur = x1
    while cur < x2:
        end = min(cur + dash, x2)
        draw.rectangle([cur, y1, end, y2], fill=color)
        cur = end + gap


def _composite_fade_line(
    canvas: Image.Image,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: tuple[int, int, int],
    fade_in_from_left: bool,
) -> Image.Image:
    """Draw a fading line by alpha-compositing segment by segment."""
    if canvas.mode != 'RGBA':
        canvas = canvas.convert('RGBA')
    segment_w = 2
    length = x2 - x1
    total = max(1, length // segment_w)
    overlay = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for i in range(total):
        frac = i / total if fade_in_from_left else 1.0 - i / total
        alpha = int(255 * frac)
        sx1 = x1 + i * segment_w
        sx2 = min(sx1 + segment_w, x2)
        if sx1 < sx2:
            odraw.rectangle([sx1, y1, sx2, y2], fill=(*color, alpha))
    return Image.alpha_composite(canvas, overlay)


def draw_logo(
    base: Image.Image,
    logo: Image.Image,
    *,
    position: str,
    align: str,
    max_width: int,
    max_height: int,
    show_lines: bool,
    line_color: tuple[int, int, int],
    line_style: str,
    line_thickness: int,
    line_margin: int,
    line_length: int,
) -> Image.Image:
    """Paste a resized logo at (position, align) on a copy of `base`.

    If `show_lines` and `align == 'center'`, draw two horizontal lines flanking
    the logo (left line fades in from left, right line fades out to right when
    style='fade').
    """
    canvas_mode_was_rgba = base.mode == 'RGBA'
    canvas = base.convert('RGBA').copy()
    resized = _resize_logo(logo.convert('RGBA'), max_width, max_height)

    lw, lh = resized.size
    lx, ly = _resolve_position(canvas.width, canvas.height, lw, lh, position, align)
    canvas.alpha_composite(resized, (lx, ly))

    if show_lines and align == 'center':
        rgb = line_color
        center_y = ly + lh // 2
        y1 = center_y - line_thickness // 2
        y2 = center_y + line_thickness // 2

        left_x2 = max(0, lx - line_margin)
        left_x1 = max(0, left_x2 - line_length)
        right_x1 = min(canvas.width, lx + lw + line_margin)
        right_x2 = min(canvas.width, right_x1 + line_length)

        draw = ImageDraw.Draw(canvas)

        if line_style == 'solid':
            if left_x1 < left_x2:
                _draw_solid_line(draw, left_x1, y1, left_x2, y2, rgb)
            if right_x1 < right_x2:
                _draw_solid_line(draw, right_x1, y1, right_x2, y2, rgb)
        elif line_style == 'dashed':
            if left_x1 < left_x2:
                _draw_dashed_line(draw, left_x1, y1, left_x2, y2, rgb)
            if right_x1 < right_x2:
                _draw_dashed_line(draw, right_x1, y1, right_x2, y2, rgb)
        elif line_style == 'fade':
            # left line: fades from transparent at far-left to solid near logo
            if left_x1 < left_x2:
                canvas = _composite_fade_line(canvas, left_x1, y1, left_x2, y2, rgb, fade_in_from_left=True)
            # right line: solid near logo, fades to transparent at far-right
            if right_x1 < right_x2:
                canvas = _composite_fade_line(
                    canvas, right_x1, y1, right_x2, y2, rgb, fade_in_from_left=False
                )

    return canvas if canvas_mode_was_rgba else canvas.convert(base.mode)
