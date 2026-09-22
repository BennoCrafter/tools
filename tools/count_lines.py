"""
Count the number of lines and characters in a folder of files.
Specify optional extensions to filter by.
"""

#!/usr/bin/env python3
import argparse
from pathlib import Path

ignored_files = [".DS_Store"]
ignored_dirs = ["__pycache__", "venv", ".git"]
ignored = ignored_files + ignored_dirs


def count_lines_for_file_path(path: Path | str) -> tuple[int, int]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines()
            return len(lines), len(content)
    except (UnicodeDecodeError, PermissionError, OSError):
        return 0, 0


def count_lines_for_path(
    path: Path,
    valid_extensions: list[str] | None,
    verbose: bool = False,
    show_file_lines: bool = False,
) -> tuple[int, int]:
    total_lines = 0
    total_chars = 0
    try:
        for item in path.iterdir():
            if item.name in ignored:
                if verbose:
                    print(f"Ignoring: {item.name}")
                continue

            if item.is_dir():
                if verbose:
                    print(f"Entering directory: {item}")
                lines, chars = count_lines_for_path(
                    item, valid_extensions, verbose, show_file_lines
                )
                total_lines += lines
                total_chars += chars
                continue

            if valid_extensions and item.suffix not in valid_extensions:
                if verbose:
                    print(f"Ignoring extension: {item.suffix} for file {item}")
                continue

            lines, chars = count_lines_for_file_path(item)
            if verbose:
                print(f"Lines in {item}: {lines}")
            if show_file_lines:
                print(f"File: {item}, Lines: {lines}, Chars: {chars}")
            total_lines += lines
            total_chars += chars
        return total_lines, total_chars
    except PermissionError:
        print(f"Warning: Permission denied accessing {path}")
        return 0, 0


def main():
    parser = argparse.ArgumentParser(
        description="Count lines of code in a path, excluding ignored files and directories."
    )
    parser.add_argument("path", type=str, help="Path to scan")
    parser.add_argument(
        "--extensions",
        "-e",
        type=str,
        nargs="+",
        help="List of valid file extensions to count (e.g. '.py .js')",
        default=None,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
        default=False,
    )
    parser.add_argument(
        "--show-file-lines",
        "-s",
        action="store_true",
        help="Show line count for each file",
        default=False,
    )

    # Parse arguments
    args = parser.parse_args()

    p = Path(args.path)
    if not p.exists():
        print(f"Error: The path '{p}' does not exist or is not a valid directory/file.")
        return

    valid_extensions = None
    if args.extensions:
        valid_extensions = [
            ext if ext.startswith(".") else f".{ext}" for ext in args.extensions
        ]
        if p.is_file() and p.suffix not in valid_extensions:
            print(
                f"Error: File '{p}' does not have a valid extension. Valid extensions: {', '.join(valid_extensions)}"
            )
            return

    if p.is_dir():
        total_lines, total_chars = count_lines_for_path(
            p, valid_extensions, args.verbose, args.show_file_lines
        )
    else:
        total_lines, total_chars = count_lines_for_file_path(p)
        if args.show_file_lines:
            print(f"File: {p}, Lines: {total_lines}, Chars: {total_chars}")

    print(f"Total lines of code in '{p}': {total_lines}")

    print(f"Total chars of code in '{p}': {total_chars}")


if __name__ == "__main__":
    main()
