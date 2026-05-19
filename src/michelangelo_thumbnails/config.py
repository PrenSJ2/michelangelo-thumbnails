"""Configuration dataclass for Michelangelo thumbnail generation."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Literal


@dataclass
class Config:
    # -------- Inputs --------
    background_image: str  # path or URL (required)
    title: str  # required
    first_circle_image: str | None = None
    first_circle_text: str | None = None
    second_circle_image: str | None = None
    second_circle_text: str | None = None
    logo_image: str | None = None
    first_background_mask: str | None = None  # pre-computed segmentation mask

    # -------- Style --------
    accent_color: str = '#FF3B30'
    use_dominant_color: bool = False
    shape: Literal['circle', 'blob', 'rounded'] = 'circle'
    shape_diameter: int = 400
    shape_border_color: str = '#FFFFFF'
    shape_border_width: int = 0
    shape_position: Literal['top-left', 'top-right', 'bottom-left', 'bottom-right'] = 'top-right'

    # -------- Canvas --------
    image_width: int = 1080
    image_height: int = 1350

    # -------- Title --------
    title_font: str = 'Herokid'
    title_font_size: int | None = None  # auto if None
    title_text_align: Literal['left', 'center', 'right'] = 'center'
    min_title_lines: int = 1

    # -------- Additional text --------
    show_additional_text: bool = False
    additional_text_content: str | None = None
    additional_text_position: Literal['top', 'above_title', 'bottom'] = 'bottom'
    additional_text_align: Literal['left', 'center', 'right'] = 'center'
    additional_text_font: str = 'Herokid'
    additional_text_font_size: int | None = None
    footer_background_color: str | None = None

    # -------- Logo --------
    show_logo: bool = False
    logo_position: Literal['top', 'above_title', 'bottom'] = 'bottom'
    logo_align: Literal['left', 'center', 'right'] = 'center'
    logo_max_width: int = 300
    logo_max_height: int = 100
    show_logo_lines: bool = False
    logo_lines_color: str = '#FFFFFF'
    logo_lines_style: Literal['solid', 'fade', 'dashed'] = 'solid'
    logo_lines_thickness: int = 2
    logo_lines_margin: int = 20
    logo_lines_length: int = 100

    # -------- Smart features --------
    use_smart_positioning: bool = True
    use_smart_overlay: bool = True
    segmenter: Literal['auto', 'rembg', 'pixian', 'none'] = 'auto'

    # -------- Effects --------
    grain_effect_intensity: float = 0.0
    grain_effect_target: Literal['none', 'background', 'whole'] = 'background'

    # -------- Reproducibility --------
    seed: int | None = None

    # -------- Caching --------
    no_cache: bool = False
    cache_dir: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Config:
        valid_names = {f.name for f in fields(cls)}
        unknown = set(data) - valid_names
        if unknown:
            raise TypeError(f'Unknown Config fields: {sorted(unknown)}')
        return cls(**data)

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}
