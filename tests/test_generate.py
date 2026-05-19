import pathlib
from io import BytesIO

import numpy as np
import pytest
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from michelangelo_thumbnails import Config, generate

FIXTURES = pathlib.Path(__file__).parent / 'fixtures'
GOLDEN = pathlib.Path(__file__).parent / 'golden'


def test_generate_minimal_returns_png_bytes():
    cfg = Config(
        background_image=str(FIXTURES / 'red64.png'),
        title='Hello',
        seed=42,
        segmenter='none',
        use_smart_positioning=False,
        use_smart_overlay=False,
    )
    data = generate(cfg)
    assert isinstance(data, bytes)
    img = Image.open(BytesIO(data))
    assert img.size == (1080, 1350)
    assert img.format == 'PNG'


def test_generate_writes_file(tmp_path):
    cfg = Config(
        background_image=str(FIXTURES / 'red64.png'),
        title='Hello',
        seed=42,
        segmenter='none',
        use_smart_positioning=False,
        use_smart_overlay=False,
    )
    out = tmp_path / 'thumb.png'
    data = generate(cfg, output_path=str(out))
    assert out.exists()
    assert isinstance(data, bytes)


def _ssim(a: bytes, b: bytes) -> float:
    img_a = np.array(Image.open(BytesIO(a)).convert('RGB'))
    img_b = np.array(Image.open(BytesIO(b)).convert('RGB'))
    return ssim(img_a, img_b, channel_axis=2)


def _common_kwargs():
    return dict(
        seed=42,
        segmenter='none',
        use_smart_positioning=False,
        use_smart_overlay=False,
    )


@pytest.mark.parametrize(
    'name,cfg_overrides',
    [
        ('basic-title-only', dict(title='LAUNCH DAY')),
        ('image-badge', dict(title='NEW', first_circle_image=str(FIXTURES / 'badge.png'))),
        (
            'two-image-badges',
            dict(
                title='PAIR',
                first_circle_image=str(FIXTURES / 'badge.png'),
                second_circle_image=str(FIXTURES / 'badge.png'),
            ),
        ),
        (
            'two-text-badges',
            dict(
                title='SALE',
                first_circle_text='NEW',
                second_circle_text='HOT',
            ),
        ),
        (
            'dominant-color',
            dict(
                title='COLORFUL',
                first_circle_image=str(FIXTURES / 'badge.png'),
                use_dominant_color=True,
            ),
        ),
        (
            'logo-and-footer',
            dict(
                title='WITH FOOTER',
                show_logo=True,
                logo_image=str(FIXTURES / 'badge.png'),
                show_additional_text=True,
                additional_text_content='SUBTITLE',
            ),
        ),
        (
            'blob-shape',
            dict(
                title='BLOB',
                first_circle_image=str(FIXTURES / 'badge.png'),
                shape='blob',
            ),
        ),
    ],
)
def test_golden(name, cfg_overrides):
    cfg = Config(
        background_image=str(FIXTURES / 'scene.png'),
        **_common_kwargs(),
        **cfg_overrides,
    )
    out = generate(cfg)
    golden_path = GOLDEN / f'{name}.png'
    if not golden_path.exists():
        golden_path.parent.mkdir(parents=True, exist_ok=True)
        golden_path.write_bytes(out)
        pytest.skip(f'Golden created at {golden_path}; re-run')
    similarity = _ssim(out, golden_path.read_bytes())
    assert similarity >= 0.99, f'SSIM {similarity:.4f} < 0.99'
