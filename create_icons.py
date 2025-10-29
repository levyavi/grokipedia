#!/usr/bin/env python3
"""Create icon files for Chrome extension with 'w -> g' design"""

from PIL import Image, ImageDraw, ImageFont

def create_icon(size, filename):
    """Create an icon image with 'w -> g' design"""
    # Create a new image with white background (better visibility)
    img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fallback to default if not available
    try:
        font_size = size // 3
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Calculate positions (centered vertically)
    text_y = size // 2
    w_x = size // 4
    g_x = size * 3 // 4
    arrow_x = size // 2
    
    # Draw 'w' on the left (blue color like Wikipedia)
    draw.text((w_x, text_y), 'w', fill=(66, 133, 244, 255), font=font, anchor='mm')
    
    # Draw arrow '->' in the middle
    arrow_thickness = max(2, size // 32)
    arrow_length = size // 6
    # Horizontal line
    draw.line([(arrow_x - arrow_length//2, text_y), (arrow_x + arrow_length//2, text_y)], 
              fill=(128, 128, 128, 255), width=arrow_thickness)
    # Arrow head
    arrow_head_size = max(arrow_length // 3, 2)
    draw.polygon([
        (arrow_x + arrow_length//2, text_y),
        (arrow_x + arrow_length//2 - arrow_head_size, text_y - arrow_head_size),
        (arrow_x + arrow_length//2 - arrow_head_size, text_y + arrow_head_size)
    ], fill=(128, 128, 128, 255))
    
    # Draw 'g' on the right (green color)
    draw.text((g_x, text_y), 'g', fill=(52, 168, 83, 255), font=font, anchor='mm')
    
    # Save as PNG
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

# Create icons in standard Chrome extension sizes
sizes = [16, 48, 128]
for size in sizes:
    create_icon(size, f'icon{size}.png')

print("All icons created successfully!")
