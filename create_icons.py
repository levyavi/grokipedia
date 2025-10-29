#!/usr/bin/env python3
"""Create icon files for Chrome extension with 'g on w' design"""

from PIL import Image, ImageDraw, ImageFont


def load_font(preferred_paths, size):
    """Load font from preferred paths with fallback"""
    for path in preferred_paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def create_icon(size, filename):
    """Create an icon with multiple small 'w' in background and one big 'g' on top"""
    img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Font paths
    regular_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "arial.ttf",
    ]
    bold_paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "arialbd.ttf",
    ]

    # Calculate sizes
    # Small 'w' letters - use about 25-30% of icon size
    small_font_size = max(int(size * 0.25), 4)
    font_w_small = load_font(regular_paths, small_font_size)
    
    # Big 'g' letter - use about 65% of icon size
    big_font_size = max(int(size * 0.65), 8)
    font_g_big = load_font(bold_paths, big_font_size)

    # Draw multiple small 'w' letters in background
    # Arrange in a grid pattern - about 2-3 rows and columns
    num_rows = 3 if size >= 48 else 2
    num_cols = 3 if size >= 48 else 2
    
    spacing_x = size // (num_cols + 1)
    spacing_y = size // (num_rows + 1)
    
    # Draw small 'w' letters in a pattern
    for row in range(num_rows):
        for col in range(num_cols):
            x = spacing_x * (col + 1)
            y = spacing_y * (row + 1)
            # Very light gray, semi-transparent
            draw.text((x, y), 'w', fill=(220, 220, 220, 150), font=font_w_small, anchor='mm')

    # Draw one big 'g' centered on top
    center_x = size // 2
    center_y = size // 2
    # Slight upward offset for visual centering (due to descender in 'g')
    offset_y = max(1, size // 32)
    draw.text((center_x, center_y - offset_y), 'g', fill=(52, 168, 83, 255), font=font_g_big, anchor='mm')

    # Save as PNG
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")


# Create icons in standard Chrome extension sizes
sizes = [16, 48, 128]
for size in sizes:
    create_icon(size, f'icon{size}.png')

print("All icons created successfully!")
