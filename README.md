# michelangelo-thumbnails

Generate Michelangelo-style thumbnails — bold title text, accent-colored
circular badges, optional product cutout. Open-source CLI + Python library +
Claude Code skill.

## Install

```bash
pip install michelangelo-thumbnails          # core
pip install michelangelo-thumbnails[smart]   # + rembg for smart positioning
```

## CLI

```bash
michelangelo generate \
  --background product.jpg \
  --title "NEW DROP" \
  --accent-color "#FF3B30" \
  --output thumb.png
```

Stdout: the absolute path of the written file. See `michelangelo generate --help`
for the full ~40-flag surface.

## Python library

```python
from michelangelo_thumbnails import Config, generate

cfg = Config(background_image='product.jpg', title='NEW DROP', accent_color='#FF3B30')
png_bytes = generate(cfg)
```

## Claude Code skill

Drop the repo into a Claude Code skills directory and Claude will pick it
up automatically when asked to generate thumbnail / poster / promo images.
See [`SKILL.md`](SKILL.md).

## Claude Code slash command

Copy [`commands/michelangelo.md`](commands/michelangelo.md) to
`~/.claude/commands/` then use:

```
/michelangelo product.jpg "NEW DROP" #FF3B30
```

## Smart segmentation

- Default: **rembg** (free, local). First run downloads ~170MB.
- Opt-in upgrade: set `PIXIAN_API_KEY=api_id:api_secret` to use Pixian instead.
- Disable entirely with `--segmenter none`.

## Development

```bash
git clone https://github.com/sebprentice/michelangelo-thumbnails
cd michelangelo-thumbnails
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,smart]"
pre-commit install
pytest
```

## License

MIT — see [LICENSE](LICENSE). Herokid font is bundled under its own permissive
license; see [src/michelangelo_thumbnails/assets/fonts/Herokid/LICENSE.txt](src/michelangelo_thumbnails/assets/fonts/Herokid/LICENSE.txt).
