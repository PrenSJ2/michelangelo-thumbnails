from dataclasses import fields

from michelangelo_thumbnails.config import Config


def test_config_has_required_fields():
    expected = {
        # Inputs
        'background_image',
        'first_circle_image',
        'first_circle_text',
        'second_circle_image',
        'second_circle_text',
        'logo_image',
        'first_background_mask',
        # Style
        'accent_color',
        'use_dominant_color',
        'shape',
        'shape_diameter',
        'shape_border_color',
        'shape_border_width',
        'shape_position',
        # Canvas
        'image_width',
        'image_height',
        # Title
        'title',
        'title_font',
        'title_font_size',
        'title_text_align',
        'min_title_lines',
        # Additional text
        'show_additional_text',
        'additional_text_content',
        'additional_text_position',
        'additional_text_align',
        'additional_text_font',
        'additional_text_font_size',
        'footer_background_color',
        # Logo
        'show_logo',
        'logo_position',
        'logo_align',
        'logo_max_width',
        'logo_max_height',
        'show_logo_lines',
        'logo_lines_color',
        'logo_lines_style',
        'logo_lines_thickness',
        'logo_lines_margin',
        'logo_lines_length',
        # Smart features
        'use_smart_positioning',
        'use_smart_overlay',
        'segmenter',
        # Effects
        'grain_effect_intensity',
        'grain_effect_target',
        # Reproducibility
        'seed',
        # Caching
        'no_cache',
        'cache_dir',
    }
    actual = {f.name for f in fields(Config)}
    missing = expected - actual
    assert not missing, f'Config missing fields: {missing}'


def test_config_defaults():
    c = Config(background_image='bg.jpg', title='hi')
    assert c.accent_color == '#FF3B30'
    assert c.image_width == 1080
    assert c.image_height == 1350
    assert c.shape == 'circle'
    assert c.shape_diameter == 400
    assert c.title_font == 'Herokid'
    assert c.title_text_align == 'center'
    assert c.use_smart_positioning is True
    assert c.use_smart_overlay is True
    assert c.segmenter == 'auto'
    assert c.grain_effect_target == 'background'
    assert c.grain_effect_intensity == 0.0


def test_config_from_dict_round_trip():
    payload = {'background_image': 'bg.jpg', 'title': 'x', 'accent_color': '#00FF00'}
    c = Config.from_dict(payload)
    assert c.accent_color == '#00FF00'
    assert c.title == 'x'


def test_config_from_dict_rejects_unknown_keys():
    import pytest

    with pytest.raises(TypeError):
        Config.from_dict({'background_image': 'bg.jpg', 'title': 'x', 'nonsense': 1})
