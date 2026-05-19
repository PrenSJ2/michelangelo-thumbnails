import pathlib
from io import BytesIO

from PIL import Image

from michelangelo_thumbnails import Config, generate

FIXTURES = pathlib.Path(__file__).parent / 'fixtures'


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
