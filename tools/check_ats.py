"""Small dependency-light checks for generated CV and cover-letter PDFs."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REQUIRED_TEXT = {
    "curriculum-vitae": (
        "First Last",
        "Location",
        "Phone",
        "Email",
        "https://example.com",
        "github-id",
        "linkedin-id",
        "Experience",
        "Education",
        "Skills",
        "Projects",
        "Certifications",
        "Dates",
        "Accomplishment",
    ),
    "cover-letter": (
        "First Last",
        "Location",
        "Phone",
        "Email",
        "https://example.com",
        "github-id",
        "linkedin-id",
        "Recipient",
        "Organization",
        "Target Role",
    ),
}


def run(command: list[str]) -> str:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(
            f"{' '.join(command)} failed with exit code {result.returncode}:\n"
            f"{result.stdout}{result.stderr}"
        )
    return result.stdout


def metadata(output: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in output.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def check_pdf(pdf: Path) -> list[str]:
    errors: list[str] = []
    stem = pdf.stem

    normal_text = run(["pdftotext", str(pdf), "-"])
    layout_text = run(["pdftotext", "-layout", str(pdf), "-"])
    for expected in REQUIRED_TEXT.get(stem, ("First Last",)):
        if expected not in normal_text:
            errors.append(f"{pdf.name}: missing normal extracted text {expected!r}")
        if expected not in layout_text:
            errors.append(f"{pdf.name}: missing layout-preserved text {expected!r}")

    info = metadata(run(["pdfinfo", str(pdf)]))
    for field in ("Title", "Author", "Subject", "Keywords"):
        if not info.get(field):
            errors.append(f"{pdf.name}: missing PDF metadata field {field}")

    image_listing = run(["pdfimages", "-list", str(pdf)])
    image_rows = [
        line
        for line in image_listing.splitlines()
        if re.match(r"^\s*\d+\s+\d+\s+\S+", line)
    ]
    if image_rows:
        errors.append(f"{pdf.name}: embedded image data found")

    font_listing = run(["pdffonts", str(pdf)])
    font_rows = [
        line
        for line in font_listing.splitlines()
        if line.strip() and not line.startswith("name ") and not line.startswith("-")
    ]
    if not font_rows:
        errors.append(f"{pdf.name}: no embedded fonts found")
    for line in font_rows:
        mapping = re.search(r"\s+(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", line)
        if mapping is None or mapping.group(3) != "yes":
            errors.append(f"{pdf.name}: font without a usable ToUnicode mapping: {line}")

    linked_xml = run(["pdftohtml", "-xml", "-stdout", "-i", str(pdf), "-"])
    if "<a href=" not in linked_xml:
        errors.append(f"{pdf.name}: no hyperlink annotations found")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_ats.py <build-directory>", file=sys.stderr)
        return 2

    build_dir = Path(sys.argv[1])
    pdfs = sorted(build_dir.glob("*.pdf"))
    expected = {f"{name}.pdf" for name in REQUIRED_TEXT}
    actual = {pdf.name for pdf in pdfs}
    errors: list[str] = []

    missing = expected - actual
    if missing:
        errors.extend(f"missing generated PDF: {name}" for name in sorted(missing))

    for pdf in pdfs:
        try:
            errors.extend(check_pdf(pdf))
        except RuntimeError as error:
            errors.append(str(error))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(f"ATS checks passed for {len(pdfs)} PDFs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
