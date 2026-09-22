"""
Combine a folder of PNG images into a single image with a spacer between each image.
"""

import os

from PIL import Image


def combine_images(image_path, spacer: int = 50):
    image_files = [f for f in os.listdir(image_path) if f.endswith(".png")]
    image_files.sort()
    if not image_files:
        return None

    images = [Image.open(os.path.join(image_path, img)) for img in image_files]

    total_width = sum(img.width for img in images) + (spacer * (len(images) - 1))
    max_height = max(img.height for img in images)

    combined_image = Image.new("RGBA", (total_width, max_height))

    x_offset = 0
    for img in images:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.width + spacer

    return combined_image


if __name__ == "__main__":
    image_path = input("Enter the path to the PNG files: ")
    image_path = ""
    result = combine_images(image_path)
    if result:
        result.save("combined_image.png")
