"""
Add GPS location to images based on a location file.
I have a digi cam which does not capture GPS location, but I love collecting metadata for the photos I take.
So I created a iPhone Shortcut which stamps my current location with time and saves it in a location file.
After each location change i log the location to a text file and take my photos.
When I'm done, I run this script to add the GPS location to the images.
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import piexif
from PIL import Image

datetime_format = "%d.%m.%Y.%H.%M.%S"

locations_path = Path(
    "digital cam/location/locations.txt"
)  # text file with lines like: 15.07.2026.17.43.44, lat;lon

print(f"Processing images from {sys.argv[1]}\n")
images_to_process_path = Path(sys.argv[1])

if not locations_path.exists():
    print("Could not find locations path. Exit.")
    exit(0)

if not images_to_process_path.exists():
    print("Could not find images path. Exit.")
    exit(0)


def to_deg(value):
    """Convert decimal degrees to EXIF format."""
    deg = int(abs(value))
    minutes = int((abs(value) - deg) * 60)
    seconds = round((((abs(value) - deg) * 60) - minutes) * 60 * 100)

    return (
        (deg, 1),
        (minutes, 1),
        (seconds, 100),
    )


def add_gps_location(input_file, output_file, latitude, longitude):
    input_file = Path(input_file)
    output_file = Path(output_file)

    if input_file.suffix.lower() in {".jpg", ".jpeg"}:
        img = Image.open(input_file)

        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: "N" if latitude >= 0 else "S",
            piexif.GPSIFD.GPSLatitude: to_deg(latitude),
            piexif.GPSIFD.GPSLongitudeRef: "E" if longitude >= 0 else "W",
            piexif.GPSIFD.GPSLongitude: to_deg(longitude),
        }

        exif_dict = {"GPS": gps_ifd}
        exif_bytes = piexif.dump(exif_dict)
        img.save(output_file, exif=exif_bytes)

    elif input_file.suffix.lower() in {".mov", ".mp4", ".m4v"}:
        if input_file.resolve() != output_file.resolve():
            shutil.copy2(input_file, output_file)

        subprocess.run(
            [
                "exiftool",
                "-overwrite_original",
                f"-GPSLatitude={latitude}",
                f"-GPSLongitude={longitude}",
                f"-Keys:GPSCoordinates={latitude} {longitude}",
                str(output_file),
            ],
            check=True,
        )
    else:
        raise ValueError(f"Unsupported file type: {input_file.suffix}")


locations = []
for location_data in open(locations_path).readlines():
    if not location_data.strip():
        continue
    date, location = location_data.split(", ")
    date_fo = datetime.strptime(date, datetime_format)
    lat, lon = location.split(";")

    locations.append((date_fo, lat, lon))

count = 0
assigned_count = 0

for image_path in images_to_process_path.iterdir():
    best_location = None

    if image_path.suffix.lower() not in {".jpg", ".jpeg", ".mov", ".mp4"}:
        continue

    count += 1
    image_creation_datetime = datetime.fromtimestamp(os.stat(image_path).st_birthtime)
    print(f"Processing {image_path.name} ({image_creation_datetime})")
    for location in locations:
        if (
            image_creation_datetime >= location[0]
        ):  # image captured after location date stamp
            best_location = location
        else:
            break

    if best_location:
        loc_date = best_location[0]
        if image_creation_datetime - loc_date > timedelta(days=1):
            print(
                f"Time range too big! Can't assign location to image ({(image_creation_datetime - loc_date)})"
            )
            continue

        print(f"  Location: {best_location[1]}, {best_location[2]}")
        add_gps_location(
            str(image_path),
            str(image_path),
            float(best_location[1]),
            float(best_location[2]),
        )
        assigned_count += 1

print(f"\n\n Assigned to {assigned_count} images out of {count}")
