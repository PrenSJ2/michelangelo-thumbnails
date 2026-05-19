"""Circle-shape pipeline: text/image circles, crops, smart placement."""

from __future__ import annotations

import logging

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from michelangelo_thumbnails.pipeline.io import resolve_font_path

try:
    LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    LANCZOS = Image.LANCZOS

log = logging.getLogger(__name__)


def create_text_circle(text: str, diameter: int, color: tuple, font_path: str | None = None) -> Image.Image:
    """Create a filled circle with centered text. Returns RGBA."""
    log.info('Creating text circle: text=%r size=%dx%d color=%s', text, diameter, diameter, color)

    # Create a square canvas with transparent background
    circle_img = Image.new('RGBA', (diameter, diameter), (0, 0, 0, 0))
    draw = ImageDraw.Draw(circle_img)

    # Draw the filled circle with the given color
    draw.ellipse([0, 0, diameter, diameter], fill=(*color, 255))

    # Load a font and calculate text size
    resolved = font_path or resolve_font_path('Herokid')
    try:
        font_size = int(diameter * 0.4)  # Adjust font size relative to circle
        font = ImageFont.truetype(resolved, font_size)
    except Exception as e:
        log.warning('Could not load font %r: %s. Using default.', resolved, e)
        font = ImageFont.load_default()

    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center the text in the circle
    text_x = (diameter - text_width) // 2
    text_y = (diameter - text_height) // 2 - bbox[1]  # Adjust for text baseline

    # Draw text in white (or contrasting color)
    text_color = (255, 255, 255)  # White text
    draw.text((text_x, text_y), text, font=font, fill=text_color)

    return circle_img


def circular_crop_with_border(
    image: Image.Image, diameter: int, border: int, border_color: tuple
) -> Image.Image:
    """Circular crop with optional border. Returns RGBA."""
    # Resize image to circle diameter if needed
    if image.size != (diameter, diameter):
        image = image.resize((diameter, diameter), LANCZOS)

    # Create circular mask for the image
    mask = Image.new('L', (diameter, diameter), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, diameter, diameter), fill=255)

    # Apply the mask to get circular image
    result = Image.new('RGBA', (diameter, diameter), (0, 0, 0, 0))
    result.paste(image.convert('RGBA'), (0, 0))
    result.putalpha(mask)

    # Add border if specified
    if border > 0:
        border_size = diameter + 2 * border
        final_image = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))

        # Draw border circle
        border_mask = Image.new('L', (border_size, border_size), 0)
        border_draw = ImageDraw.Draw(border_mask)
        border_draw.ellipse((0, 0, border_size, border_size), fill=255)
        border_circle = Image.new('RGBA', (border_size, border_size), (*border_color, 255))
        final_image.paste(border_circle, (0, 0), border_mask)
        final_image.paste(result, (border, border), result)
        return final_image

    return result


def blob_crop_with_border(image: Image.Image, diameter: int, border: int, border_color: tuple) -> Image.Image:
    """Blob-shape crop with optional border. Returns RGBA."""
    # Resize image to fit within the blob area
    if image.size != (diameter, diameter):
        image = image.resize((diameter, diameter), LANCZOS)

    # Create blob mask
    mask = Image.new('L', (diameter, diameter), 0)
    draw = ImageDraw.Draw(mask)

    # Draw a blob-like shape (irregular rounded shape)
    # Using overlapping ellipses to create organic shape
    variation = diameter // 8

    # Main blob body
    draw.ellipse((0, 0, diameter, diameter), fill=200)

    # Add some irregular bumps
    draw.ellipse((variation, 0, diameter - variation // 2, diameter - variation), fill=255)
    draw.ellipse((0, variation, diameter - variation, diameter), fill=255)

    # Smooth the mask
    mask = mask.filter(ImageFilter.GaussianBlur(radius=diameter // 40))

    # Apply the mask
    result = Image.new('RGBA', (diameter, diameter), (0, 0, 0, 0))
    result.paste(image.convert('RGBA'), (0, 0))
    result.putalpha(mask)

    # Add border if specified
    if border > 0:
        border_size = diameter + 2 * border
        final_image = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))

        # Create border blob (slightly larger)
        border_mask = Image.new('L', (border_size, border_size), 0)
        border_draw = ImageDraw.Draw(border_mask)

        # Scale up the blob shape for border
        scale = border_size / diameter
        border_draw.ellipse((0, 0, border_size, border_size), fill=200)
        border_draw.ellipse(
            (
                int(variation * scale),
                0,
                border_size - int(variation * scale / 2),
                border_size - int(variation * scale),
            ),
            fill=255,
        )
        border_draw.ellipse(
            (0, int(variation * scale), border_size - int(variation * scale), border_size), fill=255
        )

        border_mask = border_mask.filter(ImageFilter.GaussianBlur(radius=border_size // 40))

        border_blob = Image.new('RGBA', (border_size, border_size), (*border_color, 255))
        final_image.paste(border_blob, (0, 0), border_mask)
        final_image.paste(result, (border, border), result)
        return final_image

    return result


def calculate_circle_segmentation_overlap(
    circle_center_x: float,
    circle_center_y: float,
    circle_radius: float,
    segmentation_mask: Image.Image | np.ndarray,
) -> float:
    """Percentage of subject area covered by the circle. Port lines 257-309."""
    # Convert mask to numpy array if it isn't already
    if isinstance(segmentation_mask, Image.Image):
        mask_array = np.array(segmentation_mask)
    else:
        mask_array = segmentation_mask

    # Get mask dimensions
    mask_height, mask_width = mask_array.shape[:2]

    # Create a grid of coordinates
    y, x = np.ogrid[:mask_height, :mask_width]

    # Calculate distance from each pixel to circle center
    distances = np.sqrt((x - circle_center_x) ** 2 + (y - circle_center_y) ** 2)

    # Create circle mask (pixels within radius)
    circle_mask = distances <= circle_radius

    # Get alpha channel of segmentation mask (transparency)
    if len(mask_array.shape) == 3:
        # RGB image - create a binary mask where non-black pixels are considered foreground
        alpha_mask = np.any(mask_array[:, :, :3] > 10, axis=2)
    elif len(mask_array.shape) == 4:
        # RGBA image - use alpha channel
        alpha_mask = mask_array[:, :, 3] > 128  # Consider pixels with >50% opacity as foreground
    else:
        # Grayscale image
        alpha_mask = mask_array > 128

    # Calculate overlap
    overlap_pixels = np.sum(circle_mask & alpha_mask)
    circle_pixels = np.sum(circle_mask)
    subject_pixels = np.sum(alpha_mask)

    if circle_pixels == 0:
        return 0.0

    # Return percentage of SUBJECT that is covered by circle (not percentage of circle overlapping subject)
    # This ensures we limit how much of the important subject matter gets obscured
    if subject_pixels == 0:
        return 0.0

    overlap_percentage = overlap_pixels / subject_pixels
    return overlap_percentage


def place_circle(
    canvas: tuple[int, int],
    diameter: int,
    mask: Image.Image | None,
    corner: str,
    margin: int,
    avoid: list[tuple[int, int, int]],
) -> tuple[int, int]:
    """Decide where to place a circle.

    If `mask` is given, evaluate the 4 canvas corners and pick the one whose
    resulting subject overlap is closest to 5%, breaking ties by distance to
    the subject center and a small "prefer above subject" bonus.

    If `mask` is None, place at the requested corner. Either way, if the chosen
    spot collides with any (x, y, r) in `avoid` (radii sum x 1.1 minimum
    distance), try other corners in order.

    Returns (x, y) of the top-left of the circle's bounding box.
    """
    cw, ch = canvas
    radius = diameter // 2

    corners = {
        'top-left': (margin, margin),
        'top-right': (cw - diameter - margin, margin),
        'bottom-left': (margin, ch - diameter - margin),
        'bottom-right': (cw - diameter - margin, ch - diameter - margin),
    }
    fallback = corners.get(corner, corners['top-right'])

    def collides(pos):
        cx, cy = pos[0] + radius, pos[1] + radius
        for ax, ay, ar in avoid:
            acx, acy = ax + ar, ay + ar
            if ((cx - acx) ** 2 + (cy - acy) ** 2) ** 0.5 < (radius + ar) * 1.1:
                return True
        return False

    if mask is None:
        if not collides(fallback):
            return fallback
        for c in corners.values():
            if not collides(c):
                return c
        return fallback

    # Smart placement: score each corner by overlap closeness to 5% target.
    # Reference algorithm (from preview_generator.py around line 786):
    #   target = 0.05
    #   for each corner:
    #     overlap = calculate_circle_segmentation_overlap(corner_center_x, corner_center_y, radius, mask)
    #     above_bonus = -50 if corner_center_y < subject_center_y else 0
    #     score = abs(overlap - target) * 1000 + distance_to_subject * 0.1 + above_bonus
    #   pick corner with lowest score
    # Then optionally fine-tune by stepping in the away-from-subject direction.

    # Compute subject center from mask
    arr = np.array(mask)
    if arr.ndim == 3:
        binary = np.any(arr[..., :3] > 10, axis=2) if arr.shape[2] >= 3 else (arr[..., 0] > 128)
    else:
        binary = arr > 128
    ys, xs = np.where(binary)
    if len(xs) == 0:
        return fallback  # mask is empty; fall back to corner
    subject_cx = float(xs.mean())
    subject_cy = float(ys.mean())

    target = 0.05
    best = None
    for _name, (x, y) in corners.items():
        if collides((x, y)):
            continue
        ccx, ccy = x + radius, y + radius
        overlap = calculate_circle_segmentation_overlap(ccx, ccy, radius, mask)
        dist = ((ccx - subject_cx) ** 2 + (ccy - subject_cy) ** 2) ** 0.5
        above_bonus = -50.0 if ccy < subject_cy else 0.0
        score = abs(overlap - target) * 1000 + dist * 0.1 + above_bonus
        if best is None or score < best[0]:
            best = (score, (x, y))

    return best[1] if best is not None else fallback
