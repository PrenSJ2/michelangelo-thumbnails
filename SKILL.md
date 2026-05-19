---
name: michelangelo-thumbnails
description: Use when generating a Michelangelo-style thumbnail / poster / promotional image — bold title text, accent-colored circular badges, optional product cutout. Useful for product launches, Reddit/X posts, blog headers, YouTube thumbnails, app screenshots framed as marketing visuals.
---

# Michelangelo Thumbnails

You generate Michelangelo-style thumbnails by calling the `michelangelo` CLI.
Do NOT write your own PIL code; the CLI handles compositing, segmentation,
fonts, and layout.

## When to use this skill

The user asks for a thumbnail / poster / banner / promo image with:
- A bold headline
- A background image (often a product or scene)
- One or two circular "badges" containing a complementary image or short text
- Optional logo and footer text

If they want a generic image edit (crop, filter, watermark), use Bash/PIL
directly — this skill is opinionated about layout.

## Quick start

```bash
michelangelo generate \
  --background ./product.jpg \
  --title "NEW DROP" \
  --accent-color "#FF3B30" \
  --output ./thumb.png
```

Stdout will be the absolute path of the written PNG. Check stderr for warnings.

## Common recipes

### Product announcement (image + two badges)
```bash
michelangelo generate \
  --background product.jpg \
  --title "Introducing the V2" \
  --accent-color "#0A84FF" \
  --first-circle-image ./feature1.png \
  --second-circle-text "50% OFF" \
  --logo-image ./brand.png --show-logo --logo-position bottom \
  --output thumb.png
```

### Text-only badges (no product cutout)
```bash
michelangelo generate \
  --background landscape.jpg \
  --title "WEEKEND SALE" --title-text-align center \
  --first-circle-text "NEW" --second-circle-text "HOT" \
  --output sale.png
```

## All parameters

Run `michelangelo generate --help` for the full list. Important groups:

- **Inputs:** `--background`, `--first-circle-image|text`, `--second-circle-image|text`, `--logo-image`
- **Style:** `--accent-color`, `--use-dominant-color`, `--shape {circle|blob|rounded}`, `--shape-diameter`
- **Layout:** `--title-text-align`, `--shape-position`, `--logo-position`
- **Text:** `--title`, `--title-font`, `--title-font-size`, `--additional-text-*`
- **Smart features:** `--use-smart-positioning`, `--use-smart-overlay`, `--segmenter {auto|rembg|pixian|none}`
- **Effects:** `--grain-effect-intensity`, `--grain-effect-target {none|background|whole}`
- **Reproducibility:** `--seed <int>`

## Smart positioning (recommended)

By default smart positioning uses rembg (free, local). First run downloads
~170MB; subsequent runs are fast. To force-disable, pass `--segmenter none`.

For higher quality, set `PIXIAN_API_KEY` (formatted `api_id:api_secret`) and
Pixian will be used automatically.

## Loading a config from JSON

For many parameters, write a JSON file and pass `--config config.json`. CLI
flags override JSON values:

```bash
michelangelo generate --config base.json --title "Override headline"
```

## Troubleshooting

- **"Font not found"**: pass `--title-font Herokid` (bundled) or a path to a .ttf/.otf.
- **Smart positioning didn't fire**: install `pip install michelangelo-thumbnails[smart]`.
- **Pixian 401**: check `PIXIAN_API_KEY` format. Fall back: `--segmenter rembg`.
- **Output looks wrong**: re-run with `--seed 42` and compare to examples/ for a known-good baseline.
