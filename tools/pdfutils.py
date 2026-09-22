"""
A collection of utilities for working with PDF files.
"""

#!/usr/bin/env python3

from pathlib import Path

import click
from PyPDF2 import PdfMerger, PdfReader, PdfWriter


def merge_pdfs(pdf_path_list: list[Path], output_path: Path):
    pdf_merger = PdfMerger()
    pdf_path_list.sort()
    for pdf in pdf_path_list:
        if not pdf.suffix == ".pdf":
            print(f"Found invalid file: {pdf}. Skipping...")
            continue

        try:
            with open(pdf, "rb") as file:
                pdf_merger.append(file)
        except Exception as e:
            print(f"Failed to merge {pdf}: {e}")

    with open(output_path, "wb") as output_file:
        pdf_merger.write(output_file)


def invert_pdf(pdf_path: Path, output_path: Path):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for page in reversed(reader.pages):
        writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)


def rotate_pdf(pdf_path: Path, output_path: Path, angle: int, every: int, start: int):
    """Rotate specific pages in a PDF, starting from the 'start' index."""
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages, start):
        if (i + 1) % every == 0:
            page.rotate(angle)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--input",
    type=click.Path(exists=True),
    help="The path to the PDF file(s) to be inverted.",
    required=True,
)
@click.option(
    "--output",
    type=click.Path(exists=False),
    help="The path to save the output PDF(s) with inverted page order.",
    required=True,
)
def invert(input, output):
    """Invert the page order of a PDF file."""

    input = Path(input)
    output = Path(output)

    if input.is_dir():
        output.mkdir(parents=True, exist_ok=True)
        for pdf in input.glob("*.pdf"):
            output_path = output / pdf.name
            output_path.touch(exist_ok=True)

            invert_pdf(pdf, output_path)
        return

    invert_pdf(input, output)


@cli.command()
@click.option(
    "--input",
    type=click.Path(exists=True),
    help="The path to the PDF file to be rotated.",
    required=True,
    multiple=True,
)
@click.option(
    "--output",
    type=click.Path(exists=False),
    help="The path to save the output PDF with rotated pages.",
    required=True,
)
@click.option(
    "--angle",
    type=int,
    help="The angle to rotate pages (e.g., 90, 180, 270).",
    required=True,
)
@click.option("--every", type=int, help="Rotate every Nth page.", required=True)
@click.option(
    "--start", type=int, help="Start rotating from this page (1-indexed).", default=1
)
def rotate(input, output, angle, every, start):
    """Rotate specific pages in a PDF file."""
    if len(input) > 1:
        for pdf in input:
            rotate_pdf(Path(pdf), output, angle, every, start)
        return

    input = Path(input[0])
    output = Path(output)

    if input.is_dir():
        output.mkdir(parents=True, exist_ok=True)

        for pdf in input.glob("*.pdf"):
            output_path = output / pdf.name
            output_path.touch(exist_ok=True)

            rotate_pdf(pdf, output_path, angle, every, start)
        return

    print("LLLLLL")
    rotate_pdf(input, output, angle, every, start)


@cli.command()
@click.option(
    "--files",
    "-f",
    type=click.Path(exists=True),
    multiple=True,
    help="Path to the PDF files to merge.",
)
@click.option(
    "--folder", "-d", type=click.Path(exists=True), help="Path to the folder to merge."
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False),
    help="Path to save the merged PDF file.",
    required=True,
)
def merge(files, folder, output):
    """
    Merge multiple PDF files into a single PDF file.
    """

    if not files and not folder:
        raise click.UsageError("You must provide either --files or --folder.")

    if files:
        files = [Path(f) for f in files]
        merge_pdfs(files, output)
    if folder:
        folder = Path(folder)
        merge_pdfs(sorted([Path(f) for f in folder.glob("*.pdf")]), Path(output))


if __name__ == "__main__":
    cli()

# pdfutils merge -d "inp folder" -o "output.pdf"
