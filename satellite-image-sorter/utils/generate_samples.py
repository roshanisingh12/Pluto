"""
utils/generate_samples.py

Utility to generate sample satellite images with proper filename formats
and varied image formats (JPG, PNG, TIFF, WEBP) for demonstration and testing.
"""

import os
from PIL import Image, ImageDraw, ImageFont


def create_sample_images(output_dir: str = "sample_images") -> None:
    os.makedirs(output_dir, exist_ok=True)

    samples = [
        ("2026-01-15_10-30_Forest.jpg", "JPEG", (34, 139, 34), "Forest Sample\n(2026-01-15 10:30)"),
        ("2026-02-20_14-45_Water.png", "PNG", (30, 144, 255), "Water Body Sample\n(2026-02-20 14:45)"),
        ("2025-12-05_09-20_Urban.tiff", "TIFF", (128, 128, 128), "Urban Zone Sample\n(2025-12-05 09:20)"),
        ("2026-03-10_16-15_Agriculture.jpeg", "JPEG", (218, 165, 32), "Agriculture Fields\n(2026-03-10 16:15)"),
        ("2026-03-12_11-20_Barren_Land.webp", "WEBP", (210, 180, 140), "Barren Land Terrain\n(2026-03-12 11:20)"),
        ("custom_unparsed_photo.png", "PNG", (70, 130, 180), "Unparsed Filename\n(Requires Manual Metadata)"),
    ]

    for filename, img_format, bg_color, text in samples:
        img_path = os.path.join(output_dir, filename)
        img = Image.new("RGB", (640, 480), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Draw grid lines to simulate satellite sensor grid
        for x in range(0, 640, 40):
            draw.line([(x, 0), (x, 480)], fill=(bg_color[0] + 20, bg_color[1] + 20, bg_color[2] + 20), width=1)
        for y in range(0, 480, 40):
            draw.line([(0, y), (640, y)], fill=(bg_color[0] + 20, bg_color[1] + 20, bg_color[2] + 20), width=1)

        # Draw overlay box
        draw.rectangle([(80, 180), (560, 300)], fill=(0, 0, 0, 160), outline=(255, 255, 255), width=2)
        draw.text((120, 210), f"SATELLITE CAPTURE:\n{text}", fill=(255, 255, 255))

        img.save(img_path, format=img_format)
        print(f"Generated sample: {img_path}")


if __name__ == "__main__":
    create_sample_images()
