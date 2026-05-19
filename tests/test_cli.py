import json
import pathlib
import subprocess
import sys

FIXTURES = pathlib.Path(__file__).parent / 'fixtures'


def _run(*args, expect_success=True):
    proc = subprocess.run(
        [sys.executable, '-m', 'michelangelo_thumbnails.cli', *args],
        capture_output=True,
        text=True,
    )
    if expect_success:
        assert proc.returncode == 0, f'stderr:\n{proc.stderr}'
    return proc


def test_cli_help_exits_zero():
    proc = _run('--help')
    assert 'generate' in proc.stdout


def test_cli_generate_writes_file(tmp_path):
    out = tmp_path / 'out.png'
    proc = _run(
        'generate',
        '--background',
        str(FIXTURES / 'red64.png'),
        '--title',
        'CLI Test',
        '--seed',
        '42',
        '--segmenter',
        'none',
        '--no-use-smart-positioning',
        '--no-use-smart-overlay',
        '--output',
        str(out),
    )
    assert out.exists()
    assert str(out) in proc.stdout


def test_cli_generate_with_config_json(tmp_path):
    out = tmp_path / 'out.png'
    cfg = {
        'background_image': str(FIXTURES / 'red64.png'),
        'title': 'From JSON',
        'seed': 1,
        'segmenter': 'none',
        'use_smart_positioning': False,
        'use_smart_overlay': False,
    }
    cfg_path = tmp_path / 'cfg.json'
    cfg_path.write_text(json.dumps(cfg))
    _run('generate', '--config', str(cfg_path), '--output', str(out))
    assert out.exists()


def test_cli_generate_flags_override_config(tmp_path):
    out = tmp_path / 'out.png'
    cfg_path = tmp_path / 'cfg.json'
    cfg_path.write_text(
        json.dumps(
            {
                'background_image': str(FIXTURES / 'red64.png'),
                'title': 'JSON title',
                'seed': 1,
                'segmenter': 'none',
                'use_smart_positioning': False,
                'use_smart_overlay': False,
            }
        )
    )
    _run(
        'generate',
        '--config',
        str(cfg_path),
        '--title',
        'Overridden',
        '--output',
        str(out),
    )
    assert out.exists()


def test_cli_bad_args_exits_2():
    proc = subprocess.run(
        [sys.executable, '-m', 'michelangelo_thumbnails.cli', 'generate'],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
