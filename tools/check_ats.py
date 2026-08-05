"""Small dependency-light checks for generated CV and cover-letter PDFs."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REQUIRED_TEXT = {
    "template": {
        "curriculum-vitae": (
            "First Last",
            "Location",
            "Phone",
            "Email",
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
            "Recipient",
            "Target Role",
        ),
    },
    "demo": {
        "curriculum-vitae": (
            "John Doe",
            "Berlin, Germany",
            "+49 30 555 0123",
            "john.doe@example.com",
            "Experience",
            "Education",
            "Skills",
            "Projects",
            "Certifications",
            "Senior DevOps Engineer",
            "Lorem ipsum",
        ),
        "cover-letter": (
            "John Doe",
            "Berlin, Germany",
            "+49 30 555 0123",
            "john.doe@example.com",
            "Hiring Team",
            "DevOps Engineer",
            "Acme Cloud GmbH",
            "Lorem ipsum",
        ),
    },
}

# The intentional centered-dot separator in the header comes from LaTeX's
# symbol font. It is decorative and is the only expected font without a
# ToUnicode mapping; all text fonts must still pass the mapping check below.
DECORATIVE_UNMAPPED_FONTS = ("CMSY10",)


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


def normalize_text(output: str) -> str:
    """Make PDF text extraction comparable across line-wrapping engines."""
    return " ".join(output.split())


def check_pdf(pdf: Path, required_text: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    stem = pdf.stem

    normal_text = normalize_text(run(["pdftotext", str(pdf), "-"]))
    layout_text = normalize_text(run(["pdftotext", "-layout", str(pdf), "-"]))
    for expected in required_text:
        expected = normalize_text(expected)
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
        font_name = line.split()[0]
        decorative = any(
            font_name == allowed or font_name.endswith(f"+{allowed}")
            for allowed in DECORATIVE_UNMAPPED_FONTS
        )
        if mapping is None or (mapping.group(3) != "yes" and not decorative):
            errors.append(f"{pdf.name}: font without a usable ToUnicode mapping: {line}")

    linked_xml = run(["pdftohtml", "-xml", "-stdout", "-i", str(pdf), "-"])
    if "<a href=" not in linked_xml:
        errors.append(f"{pdf.name}: no hyperlink annotations found")

    return errors


def main() -> int:
    if len(sys.argv) not in (2, 4) or (len(sys.argv) == 4 and sys.argv[2] != "--profile"):
        print("usage: check_ats.py <build-directory> [--profile template|demo]", file=sys.stderr)
        return 2

    build_dir = Path(sys.argv[1])
    profile = sys.argv[3] if len(sys.argv) == 4 else "template"
    if profile not in REQUIRED_TEXT:
        print(f"unknown profile: {profile}", file=sys.stderr)
        return 2

    pdfs = sorted(build_dir.glob("*.pdf"))
    required_text = REQUIRED_TEXT[profile]
    fallback_text = ("First Last",) if profile == "template" else ("John Doe",)
    expected = {f"{name}.pdf" for name in required_text}
    actual = {pdf.name for pdf in pdfs}
    errors: list[str] = []

    missing = expected - actual
    if missing:
        errors.extend(f"missing generated PDF: {name}" for name in sorted(missing))

    for pdf in pdfs:
        try:
            errors.extend(check_pdf(pdf, required_text.get(pdf.stem, fallback_text)))
        except RuntimeError as error:
            errors.append(str(error))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(f"ATS checks passed for {len(pdfs)} PDFs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
