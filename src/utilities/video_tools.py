"""Video conversion helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .ffmpeg_config import get_ffmpeg_executable


VIDEO_OUTPUT_FORMATS = ("mp4", "mkv", "webm", "mov", "avi")
AUDIO_OUTPUT_FORMATS = ("mp3", "wav", "m4a", "flac", "ogg")


def convert_video(input_file: str, output_file: str, format_name: str = "mp4") -> str:
    """Convert a video file to a video or audio-only format via ffmpeg."""
    input_path = Path(input_file)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    converted_path = output_path.with_suffix(f".{format_name.lstrip('.')}")

    command = [
        get_ffmpeg_executable(),
        "-y",
        "-i",
        str(input_path),
        *(["-vn"] if format_name.lstrip(".").lower() in AUDIO_OUTPUT_FORMATS else []),
        str(converted_path),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        if error.returncode in (-1073741521, 0xC000012F):
            raise RuntimeError(
                "FFmpeg could not start because its shared-build executable has a missing or "
                "incompatible runtime DLL. Set FFMPEG_DIR to a complete static FFmpeg build, "
                "not a full_build-shared folder."
            ) from error

        details = (error.stderr or "").strip()
        if "Output file does not contain any stream" in details:
            raise RuntimeError(
                "This input contains no audio stream, so it cannot be converted to an audio "
                "format. Choose a video file with audio or download an audio format first."
            ) from error
        raise RuntimeError(
            f"FFmpeg could not convert the video{': ' + details if details else '.'}"
        ) from error

    return str(converted_path)
