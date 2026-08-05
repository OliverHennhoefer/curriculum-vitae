#!/usr/bin/env python3
"""Install the CV's Google Fonts into the current user's font directory.

This is intentionally an opt-in helper for ``make fonts``. It does not put
font binaries in the repository and does not run during a normal build.
"""

from __future__ import annotations

import argparse
import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


GOOGLE_FONTS_RAW = "https://raw.githubusercontent.com/google/fonts"


@dataclass(frozen=True)
class FontFile:
    family: str
    directory: str
    revision: str
    filename: str

    @property
    def url(self) -> str:
        return "/".join(
            (
                GOOGLE_FONTS_RAW,
                self.revision,
                "ofl",
                self.directory,
                quote(self.filename, safe=""),
            )
        )


# These are immutable Google Fonts repository revisions rather than a moving
# ``main`` URL. Keeping the revisions here makes repeated local builds use the
# same font binaries, while still allowing an intentional update in one small,
# reviewable change.
FONT_FILES = (
    FontFile(
        "Source Sans 3",
        "sourcesans3",
        "914ec116571b1162d886aa402e715552221f0b77",
        "SourceSans3[wght].ttf",
    ),
    FontFile(
        "Source Sans 3",
        "sourcesans3",
        "914ec116571b1162d886aa402e715552221f0b77",
        "SourceSans3-Italic[wght].ttf",
    ),
    FontFile(
        "Roboto",
        "roboto",
        "1c627bfa375fc51cf86fabeca4f6e08a95f0aa5c",
        "Roboto[wdth,wght].ttf",
    ),
    FontFile(
        "Roboto",
        "roboto",
        "1c627bfa375fc51cf86fabeca4f6e08a95f0aa5c",
        "Roboto-Italic[wdth,wght].ttf",
    ),
)


def user_font_directory() -> Path:
    """Return a font directory writable by the current user."""

    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        base = (
            Path(local_app_data)
            if local_app_data
            else Path.home() / "AppData" / "Local"
        )
        return base / "Microsoft" / "Windows" / "Fonts"

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Fonts"

    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg_data_home) if xdg_data_home else Path.home() / ".local" / "share"
    return base / "fonts" / "curriculum-vitae"


def download_font(font: FontFile, destination: Path, force: bool) -> None:
    if destination.exists() and not force:
        print(f"[skip]     {destination.name} already exists")
        return

    print(f"[download] {font.family}: {font.filename}")
    request = Request(
        font.url,
        headers={"User-Agent": "curriculum-vitae font installer"},
    )
    temporary_path: Path | None = None
    try:
        with urlopen(request, timeout=90) as response:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=f".{destination.name}.",
                suffix=".download",
                dir=destination.parent,
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                shutil.copyfileobj(response, temporary_file)
        os.replace(temporary_path, destination)
    except (HTTPError, URLError, OSError) as error:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise RuntimeError(f"could not download {font.filename}: {error}") from error


def register_windows_fonts(installed: Iterable[tuple[FontFile, Path]]) -> None:
    """Register per-user fonts on Windows without administrator access."""

    if os.name != "nt":
        return

    import winreg

    registry_path = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"
    with winreg.CreateKeyEx(
        winreg.HKEY_CURRENT_USER,
        registry_path,
        0,
        winreg.KEY_SET_VALUE,
    ) as registry_key:
        for font, path in installed:
            value_name = f"Curriculum Vitae - {font.family} - {font.filename}"
            winreg.SetValueEx(
                registry_key,
                value_name,
                0,
                winreg.REG_SZ,
                str(path),
            )

    # Tell running applications that the per-user font set changed. New
    # LuaLaTeX processes will see the fonts even when a host application does
    # not react to this broadcast.
    try:
        result = ctypes.c_ulong()
        ctypes.windll.user32.SendMessageTimeoutW(
            ctypes.c_void_p(0xFFFF),
            0x001D,  # WM_FONTCHANGE
            0,
            0,
            0x0002,  # SMTO_ABORTIFHUNG
            1000,
            ctypes.byref(result),
        )
    except (AttributeError, OSError):
        pass


def refresh_font_caches(font_directory: Path) -> None:
    """Refresh caches when the host provides the corresponding utilities."""

    commands: list[list[str]] = []
    if os.name != "nt" and shutil.which("fc-cache"):
        commands.append(["fc-cache", "-f", str(font_directory)])
    if shutil.which("luaotfload-tool"):
        commands.append(["luaotfload-tool", "--update", "--force"])

    for command in commands:
        print(f"[refresh]  {' '.join(command)}")
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            print(
                f"warning: {' '.join(command)} exited with "
                f"status {completed.returncode}; restart the TeX editor and retry",
                file=sys.stderr,
            )

    if not commands:
        print(
            "warning: no font-cache tool was found; restart the TeX editor "
            "before compiling",
            file=sys.stderr,
        )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install the pinned Google Fonts used by the CV locally."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="redownload and replace existing font files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show the download and install locations without changing anything",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    font_directory = user_font_directory()

    print(f"Font directory: {font_directory}")
    if arguments.dry_run:
        for font in FONT_FILES:
            print(f"[dry-run]  {font.url}")
        return 0

    font_directory.mkdir(parents=True, exist_ok=True)
    installed: list[tuple[FontFile, Path]] = []
    for font in FONT_FILES:
        destination = font_directory / font.filename
        download_font(font, destination, arguments.force)
        installed.append((font, destination))

    register_windows_fonts(installed)
    refresh_font_caches(font_directory)
    print("Fonts installed. Rebuild with `make clean && make`.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
