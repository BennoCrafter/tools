#!/usr/bin/env python3
"""

Batch-downscale every video in an input folder
"""

"""
to a maximum height (default
1800px) and write the results to an output folder, preserving:

Requirements:
  - ffmpeg and ffprobe must be installed and on PATH.

Usage:
  python3 downscale_videos.py /path/to/input_folder /path/to/output_folder
  python3 downscale_videos.py IN OUT --height 1800 --crf 18 --preset slow
  python3 downscale_videos.py IN OUT --recursive

(vibe coded)
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".m4v",
    ".mkv",
    ".avi",
    ".webm",
    ".wmv",
    ".flv",
    ".mpg",
    ".mpeg",
    ".ts",
    ".3gp",
}


def run(cmd):
    """Run a subprocess command, raising with stderr on failure."""
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({' '.join(cmd)}):\n{result.stderr.decode(errors='ignore')}"
        )
    return result.stdout


def get_video_height(path: Path) -> int:
    """Return the height (in pixels) of the first video stream, or -1 if unknown."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=height",
        "-of",
        "json",
        str(path),
    ]
    out = run(cmd)
    data = json.loads(out)
    streams = data.get("streams", [])
    if not streams or "height" not in streams[0]:
        return -1
    return int(streams[0]["height"])


def _build_downscale_cmd(
    src: Path,
    dst: Path,
    target_height: int,
    crf: int,
    preset: str,
    drop_data_streams: bool,
):
    scale_filter = f"scale=-2:{target_height}"
    cmd = ["ffmpeg", "-y", "-i", str(src)]

    cmd += ["-map", "0"]
    if drop_data_streams:
        # Exclude data/timecode streams (e.g. GoPro/Canon "tmcd" or gpmd tracks).
        # These aren't picture/sound content, so nothing meaningful is lost,
        # but many containers reject them once re-muxed explicitly.
        cmd += ["-map", "-0:d"]

    cmd += [
        "-map_metadata",
        "0",  # copy global + stream metadata
        "-map_chapters",
        "0",  # copy chapters if present
        "-vf",
        scale_filter,
        "-c:v",
        "libx264",
        "-crf",
        str(crf),
        "-preset",
        preset,
        "-c:a",
        "copy",
        "-c:s",
        "copy",
        "-movflags",
        "use_metadata_tags",
        str(dst),
    ]
    return cmd


def downscale_video(src: Path, dst: Path, target_height: int, crf: int, preset: str):
    """Re-encode video, scaling to target_height, preserving audio/subs/metadata."""
    try:
        # First attempt: keep everything except opaque data streams.
        run(
            _build_downscale_cmd(
                src, dst, target_height, crf, preset, drop_data_streams=True
            )
        )
    except RuntimeError:
        # Fallback: some containers still choke on subtitle/chapter combos.
        # Retry with just video + audio, which always works.
        scale_filter = f"scale=-2:{target_height}"
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-map",
            "0:v:0",
            "-map",
            "0:a?",
            "-map_metadata",
            "0",
            "-vf",
            scale_filter,
            "-c:v",
            "libx264",
            "-crf",
            str(crf),
            "-preset",
            preset,
            "-c:a",
            "copy",
            "-movflags",
            "use_metadata_tags",
            str(dst),
        ]
        run(cmd)


def copy_video(src: Path, dst: Path):
    """No re-encode needed; straight copy preserves everything exactly."""
    shutil.copy2(src, dst)


def process_folder(
    input_dir: Path,
    output_dir: Path,
    target_height: int,
    crf: int,
    preset: str,
    recursive: bool,
    overwrite: bool,
):
    output_dir.mkdir(parents=True, exist_ok=True)

    pattern = "**/*" if recursive else "*"
    files = sorted(
        p
        for p in input_dir.glob(pattern)
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
    )

    if not files:
        print(f"No video files found in {input_dir}")
        return

    print(f"Found {len(files)} video file(s). Target max height: {target_height}px\n")

    for i, src in enumerate(files, 1):
        rel = src.relative_to(input_dir)
        dst = output_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        if dst.exists() and not overwrite:
            print(f"[{i}/{len(files)}] SKIP (exists): {rel}")
            continue

        print(f"[{i}/{len(files)}] Processing: {rel}")
        try:
            height = get_video_height(src)
        except Exception as e:
            print(f"    ! Could not read video info, copying as-is. ({e})")
            copy_video(src, dst)
            shutil.copystat(src, dst)
            continue

        try:
            if 0 < height <= target_height:
                print(
                    f"    Height {height}px <= {target_height}px -> copying, no re-encode"
                )
                copy_video(src, dst)
            else:
                print(f"    Height {height}px -> downscaling to {target_height}px")
                downscale_video(src, dst, target_height, crf, preset)
            # Preserve original file timestamps on the output file
            shutil.copystat(src, dst)
        except Exception as e:
            print(f"    ! FAILED: {e}")
            if dst.exists():
                dst.unlink()

    print("\nDone.")


def main():
    parser = argparse.ArgumentParser(
        description="Batch-downscale videos while preserving metadata."
    )
    parser.add_argument(
        "input_folder", type=Path, help="Folder containing source videos"
    )
    parser.add_argument(
        "output_folder", type=Path, help="Folder to write downscaled videos to"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1800,
        help="Maximum output height in pixels (default: 1800)",
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=18,
        help="x264 CRF quality, lower = better quality/larger file (default: 18)",
    )
    parser.add_argument(
        "--preset",
        type=str,
        default="slow",
        choices=[
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
        ],
        help="x264 encoding preset (default: slow)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recurse into subfolders of the input folder",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite files already present in the output folder",
    )
    args = parser.parse_args()

    if not args.input_folder.is_dir():
        print(
            f"Error: input folder does not exist: {args.input_folder}", file=sys.stderr
        )
        sys.exit(1)

    # Sanity check ffmpeg/ffprobe are available
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            print(
                f"Error: '{tool}' not found on PATH. Please install ffmpeg.",
                file=sys.stderr,
            )
            sys.exit(1)

    process_folder(
        args.input_folder,
        args.output_folder,
        args.height,
        args.crf,
        args.preset,
        args.recursive,
        args.overwrite,
    )


if __name__ == "__main__":
    main()
