"""Top-level orchestration: Config -> composited PNG bytes."""

from __future__ import annotations

import logging
import pathlib
from io import BytesIO

from PIL import Image

from michelangelo_thumbnails.config import Config
from michelangelo_thumbnails.pipeline import background, circles, segmentation, text
from michelangelo_thumbnails.pipeline import io as io_helpers
from michelangelo_thumbnails.pipeline import logo as logo_pipe

log = logging.getLogger(__name__)


def generate(cfg: Config, output_path: str | None = None) -> bytes:
    """Generate a thumbnail. Returns PNG bytes; writes to output_path if given."""
    # 1. Resolve inputs
    bg = io_helpers.fetch_image(cfg.background_image)

    # 2. Background
    bg = background.enhance_image(bg)
    bg = background.resize_cover(bg, (cfg.image_width, cfg.image_height))

    # 3. Segmentation
    if cfg.use_smart_positioning or cfg.use_smart_overlay:
        mask = segmentation.segment(bg, mode=cfg.segmenter, no_cache=cfg.no_cache, cache_dir=cfg.cache_dir)
    else:
        mask = None

    # 4. Grain (background)
    if cfg.grain_effect_target in ('background', 'whole'):
        bg = background.add_grain(bg, intensity=cfg.grain_effect_intensity, seed=cfg.seed)

    # 5-8. Circles
    placed: list[tuple[int, int, int]] = []
    canvas = bg.convert('RGBA')
    for _slot, img_src, text_src, corner in [
        ('first', cfg.first_circle_image, cfg.first_circle_text, cfg.shape_position),
        ('second', cfg.second_circle_image, cfg.second_circle_text, _opposite_corner(cfg.shape_position)),
    ]:
        if not img_src and not text_src:
            continue
        smart_mask = mask if cfg.use_smart_positioning else None
        diameter = cfg.shape_diameter if img_src else int(cfg.shape_diameter * 0.65)
        x, y = circles.place_circle(
            canvas=(cfg.image_width, cfg.image_height),
            diameter=diameter,
            mask=smart_mask,
            corner=corner,
            margin=80,
            avoid=placed,
        )
        circle_img = _build_circle_image(img_src, text_src, diameter, cfg)
        canvas.paste(circle_img, (x, y), circle_img)
        placed.append((x, y, diameter // 2))

    # 9. Title
    title_color = _title_color(cfg, placed_circle_image=_first_circle_resolved(cfg))
    base_size = cfg.title_font_size or _default_title_size(cfg)
    bottom_reserve = (
        320
        if (
            cfg.show_additional_text
            and cfg.additional_text_content
            and cfg.additional_text_position == 'bottom'
        )
        else 0
    )
    canvas = text.draw_title(
        canvas.convert('RGB'),
        title=cfg.title,
        font_path=io_helpers.resolve_font_path(cfg.title_font),
        font_size=base_size,
        color=title_color,
        align=cfg.title_text_align,
        bottom_reserve=bottom_reserve,
    )

    # 10. Additional text
    if cfg.show_additional_text and cfg.additional_text_content:
        bar_color = (
            io_helpers.hex_to_rgb(cfg.footer_background_color) if cfg.footer_background_color else None
        )
        canvas = text.draw_additional_text(
            canvas,
            text=cfg.additional_text_content,
            font_path=io_helpers.resolve_font_path(cfg.additional_text_font),
            font_size=cfg.additional_text_font_size or 50,
            color=io_helpers.hex_to_rgb(cfg.accent_color),
            align=cfg.additional_text_align,
            position=cfg.additional_text_position,
            bar_color=bar_color,
        )

    # 11. Logo
    if cfg.show_logo and cfg.logo_image:
        logo_img = io_helpers.fetch_image(cfg.logo_image).convert('RGBA')
        canvas = logo_pipe.draw_logo(
            canvas,
            logo_img,
            position=cfg.logo_position,
            align=cfg.logo_align,
            max_width=cfg.logo_max_width,
            max_height=cfg.logo_max_height,
            show_lines=cfg.show_logo_lines,
            line_color=io_helpers.hex_to_rgb(cfg.logo_lines_color),
            line_style=cfg.logo_lines_style,
            line_thickness=cfg.logo_lines_thickness,
            line_margin=cfg.logo_lines_margin,
            line_length=cfg.logo_lines_length,
        )

    # 12. Grain (whole)
    if cfg.grain_effect_target == 'whole':
        canvas = background.add_grain(canvas, intensity=cfg.grain_effect_intensity, seed=cfg.seed)

    # 13. Flatten and 14. encode
    if canvas.mode == 'RGBA':
        flat = Image.new('RGB', canvas.size, (255, 255, 255))
        flat.paste(canvas, mask=canvas.split()[-1])
        canvas = flat

    buf = BytesIO()
    canvas.save(buf, format='PNG', optimize=True)
    data = buf.getvalue()

    if output_path:
        pathlib.Path(output_path).write_bytes(data)
    return data


def _opposite_corner(corner: str) -> str:
    return {
        'top-left': 'bottom-right',
        'top-right': 'bottom-left',
        'bottom-left': 'top-right',
        'bottom-right': 'top-left',
    }.get(corner, 'bottom-left')


def _build_circle_image(img_src, text_src, diameter, cfg):
    if img_src:
        img = io_helpers.fetch_image(img_src)
        if cfg.shape == 'blob':
            return circles.blob_crop_with_border(
                img, diameter, cfg.shape_border_width, io_helpers.hex_to_rgb(cfg.shape_border_color)
            )
        return circles.circular_crop_with_border(
            img, diameter, cfg.shape_border_width, io_helpers.hex_to_rgb(cfg.shape_border_color)
        )
    return circles.create_text_circle(text_src, diameter, io_helpers.hex_to_rgb(cfg.accent_color))


def _first_circle_resolved(cfg):
    if cfg.first_circle_image:
        try:
            return io_helpers.fetch_image(cfg.first_circle_image)
        except Exception:
            return None
    return None


def _title_color(cfg, placed_circle_image):
    if cfg.use_dominant_color and placed_circle_image is not None:
        return text.dominant_color(placed_circle_image)
    return io_helpers.hex_to_rgb(cfg.accent_color)


def _default_title_size(cfg) -> int:
    """Match preview_generator.py default (~105 at 1080x1350)."""
    return int(cfg.image_width * 0.097)
