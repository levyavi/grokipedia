#!/usr/bin/env python3
"""Create icon files for Chrome extension with 'g on w' design"""

from PIL import Image, ImageDraw, ImageFont

def create_icon(size, filename):
    """Create an icon image with bold 'g' on top of light 'w' design"""
    # Create a new image with white background
    img = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fallback to default if not available
    try:
        # Large font size for the letters to fill most of the space
        font_size = int(size * 0.65)
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
        font_bold = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
            font_bold = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            # If bold font not available, use regular with thicker stroke
            font = ImageFont.load_default()
            font_bold = font
    
    # Center position
    center_x = size // 2
    center_y = size // 2
    
    # Draw light 'w' as background/base (light gray, semi-transparent)
    draw.text((center_x, center_y), 'w', fill=(200, 200, 200, 200), font=font, anchor='mm')
    
    # Draw bold 'g' on top (bold, darker, more opaque)
    # Slightly offset upward for better visual separation
    draw.text((center_x, center_y - size // 12), 'g', fill=(52, 168, 83, 255), font=font_bold, anchor='mm')
    
    # If bold font not available, draw the 'g' with a thicker outline
    if font_bold == font:
        # Draw multiple slightly offset versions to simulate bold
        for offset_x in range(-1, 2):
            for offset_y in range(-1, 2):
                if offset_x != 0 or offset_y != 0:
                    draw.text((center_x + offset_x, center_y - size // 12 + offset_y), 
                             'g', fill=(52, 168, 83, 200), font=font, anchor='mm')
        # Draw the main 'g' on top
        draw.text((center_x, center_y - size // 12), 'g', fill=(52, 168, 83, 255), font=font, anchor='mm')
    
    # Save as PNG
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

# Create icons in standard Chrome extension sizes
sizes = [16, 48, 128]
for size in sizes:
    create_icon(size, f'icon{size}.png')

print("All icons created successfully!")
