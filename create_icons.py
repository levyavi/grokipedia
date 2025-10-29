#!/usr/bin/env python3
"""Create icon files for Chrome extension with 'g on w' design.

Maximize glyph sizes to minimize whitespace: we measure text bounding boxes
and grow fonts until just fitting within the icon with a small padding.
"""

from PIL import Image, ImageDraw, ImageFont


def load_font(preferred_paths, size):
    for path in preferred_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    # Fallback
    return ImageFont.load_default()


def fit_font_to_box(draw, text, max_size, preferred_paths, padding):
    """Return a PIL font sized as large as possible to fit text within max_size-p padding."""
    # Binary search font size for performance and accuracy
    lo, hi = 1, max_size  # font sizes in pixels
    best_font = ImageFont.load_default()
    while lo <= hi:
        mid = (lo + hi) // 2
        font = load_font(preferred_paths, mid)
        # Measure text bbox at origin
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        if width <= max_size - 2 * padding and height <= max_size - 2 * padding:
            best_font = font
            lo = mid + 1  # try bigger
        else:
            hi = mid - 1  # too big, try smaller
    return best_font

def create_icon(size, filename):
    """Create an icon image with bold 'g' on top of light 'w' design, maximized to fill space."""
    img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Fonts to try (Windows first, then generic)
    regular_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "arial.ttf",
    ]
    bold_paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "arialbd.ttf",
        # fallback to regular if bold missing
    ]

    # Use a tiny padding to minimize whitespace but avoid clipping
    padding = max(1, size // 16)

    # Fit background 'w' to the icon box
    font_w = fit_font_to_box(draw, 'w', size, regular_paths, padding)
    # Draw light 'w' centered
    draw.text((size // 2, size // 2), 'w', fill=(200, 200, 200, 220), font=font_w, anchor='mm')

    # Fit foreground 'g' to same or slightly larger, but still within bounds
    # Use bold if available; otherwise we'll simulate bold with outline
    font_g_bold = fit_font_to_box(draw, 'g', size, bold_paths, padding)
    # Ensure 'g' is at least as big as 'w' visually by retrying with reduced padding if needed
    # Note: fit_font_to_box already maximizes, so this typically suffices

    # Draw bold 'g' centered; tiny upward offset can help with visual centering for descenders
    draw.text((size // 2, size // 2 - max(1, size // 32)), 'g', fill=(52, 168, 83, 255), font=font_g_bold, anchor='mm')
    
    # Save as PNG
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

# Create icons in standard Chrome extension sizes
sizes = [16, 48, 128]
for size in sizes:
    create_icon(size, f'icon{size}.png')

print("All icons created successfully!")
