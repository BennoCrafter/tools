"""
Round the corners of an image to a specified radius and save the result.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw


def round_corners(image_path: Path, radius: int, output_path: Path) -> Image.Image:
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size

    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, w, h), radius, fill=255)

    output = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    output.paste(img, mask=mask)

    output.save(output_path)
    return output


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: round_corner_to_image.py <input_image> <radius> <output_image>")
        sys.exit(1)

    round_corners(Path(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3]))
