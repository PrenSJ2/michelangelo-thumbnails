---
description: Generate a Michelangelo-style thumbnail
argument-hint: <background> <title> [accent_color]
allowed-tools: Bash
---

Generate a Michelangelo-style thumbnail with the `michelangelo` CLI.

Arguments: $ARGUMENTS

Parse the arguments as: `<background_image_path_or_url> "<title>" [accent_color_hex]`.
If accent_color is omitted, default to `#FF3B30`.

Run:

```bash
michelangelo generate \
  --background <background> \
  --title "<title>" \
  --accent-color <accent_color> \
  --output ./michelangelo-$(date +%s).png
```

Print the output path. If the CLI is not installed, instruct the user to run
`pip install michelangelo-thumbnails[smart]`.
