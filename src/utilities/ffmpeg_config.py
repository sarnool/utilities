"""Shared configuration for FFmpeg-dependent utilities."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOTENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(DOTENV_PATH, override=True)


def get_ffmpeg_dir() -> Path:
    if not DOTENV_PATH.is_file():
        raise RuntimeError(f"FFmpeg configuration file is missing: {DOTENV_PATH}")

    configured_dir = os.getenv("FFMPEG_DIR", "").strip()
    if not configured_dir:
        raise RuntimeError(f"Set FFMPEG_DIR in {DOTENV_PATH}.")

    ffmpeg_dir = Path(configured_dir).expanduser()
    if not ffmpeg_dir.is_absolute():
        ffmpeg_dir = (PROJECT_ROOT / ffmpeg_dir).resolve()
    if not ffmpeg_dir.is_dir():
        raise FileNotFoundError(f"Configured FFMPEG_DIR does not exist: {ffmpeg_dir}")

    executable = ffmpeg_dir / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    if not executable.is_file():
        raise FileNotFoundError(f"FFmpeg executable was not found: {executable}")
    return ffmpeg_dir


def get_ffmpeg_executable() -> str:
    ffmpeg_dir = get_ffmpeg_dir()
    executable = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    return str(ffmpeg_dir / executable)


def configure_ffmpeg_path() -> Path:
    ffmpeg_dir = get_ffmpeg_dir()
    path_entries = os.environ.get("PATH", "").split(os.pathsep)
    if str(ffmpeg_dir) not in path_entries:
        os.environ["PATH"] = os.pathsep.join([str(ffmpeg_dir), *path_entries])
    return ffmpeg_dir