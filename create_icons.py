#!/usr/bin/env python3
"""Create icon files for Chrome extension with 'w -> g' design"""

from PIL import Image, ImageDraw, ImageFont

def create_icon(size, filename):
    """Create an icon image with 'w -> g' design"""
    # Create a new image with white background (better visibility)
    img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fallback to default if not available
    # Use larger font to fill more space
    try:
        font_size = int(size * 0.5)  # 50% of icon size for bigger text
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Calculate positions - spread out more to edges, minimize empty space
    text_y = size // 2
    # Move 'w' closer to left edge, 'g' closer to right edge
    w_x = size // 6  # Closer to left
    g_x = size * 5 // 6  # Closer to right
    arrow_x = size // 2
    
    # Draw 'w' on the left (blue color like Wikipedia)
    draw.text((w_x, text_y), 'w', fill=(66, 133, 244, 255), font=font, anchor='mm')
    
    # Draw arrow '->' in the middle - make it smaller to allow bigger text
    arrow_thickness = max(1, size // 40)
    arrow_length = size // 8
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
