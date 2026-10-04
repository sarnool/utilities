"""Audio conversion helpers."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .ffmpeg_config import get_ffmpeg_executable


def convert_audio(input_file: str, output_file: str, format_name: str = "mp3") -> str:
    """Convert an audio file to the requested format via ffmpeg."""
    input_path = Path(input_file)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        get_ffmpeg_executable(),
        "-y",
        "-i",
        str(input_path),
        str(output_path.with_suffix(f".{format_name.lstrip('.')}")),
    ]

    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return str(output_path.with_suffix(f".{format_name.lstrip('.')}"))


def main():
    print("Audio conversion utility")


if __name__ == "__main__":
    main()
