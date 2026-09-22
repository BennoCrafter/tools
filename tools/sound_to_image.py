"""
Create a video from a photo and an mp3, lasting a given duration.
(vibe coded)
"""

import argparse
import os
import subprocess


def create_video(audio_file, image_file, duration, output_file=None, start=0.0):
    if output_file is None:
        output_file = os.path.splitext(image_file)[0] + ".mp4"

    ffmpeg_cmd = [
        "ffmpeg",
        "-loop",
        "1",
        "-i",
        image_file,
        "-ss",
        str(start),
        "-i",
        audio_file,
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-c:v",
        "libx264",
        "-tune",
        "stillimage",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-pix_fmt",
        "yuv420p",
        "-t",
        str(duration),
        "-y",
        output_file,
    ]

    subprocess.run(ffmpeg_cmd, check=True)
    print(f"Successfully created {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a video from a photo and an mp3, lasting a given duration."
    )
    parser.add_argument("mp3", help="Path to the mp3 file")
    parser.add_argument("photo", help="Path to the photo file")
    parser.add_argument(
        "duration", type=float, help="Duration of the resulting video in seconds"
    )
    parser.add_argument(
        "-o", "--output", help="Path to the output video file", default=None
    )
    parser.add_argument(
        "-s",
        "--start",
        type=float,
        default=0.0,
        help="Where in the mp3 to start (seconds)",
    )
    args = parser.parse_args()

    create_video(args.mp3, args.photo, args.duration, args.output, args.start)
