"""YouTube/media download helpers."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, cast

import yt_dlp

from .ffmpeg_config import get_ffmpeg_dir


class FormatListingError(RuntimeError):
    """Raised when media formats cannot be retrieved for a URL."""


def describe_media_error(error: Exception, operation: str = "format listing") -> str:
    """Return a concise, actionable message for a media operation failure."""
    message = str(error)
    lowered_message = message.lower()
    if "certificate_verify_failed" in lowered_message or "ssl" in lowered_message:
        return "The secure connection to YouTube failed. Check your proxy or certificate settings."
    if "cookie" in lowered_message or "cookies" in lowered_message:
        return "Chrome cookies could not be read. Close Chrome or allow yt-dlp to access browser cookies."
    if "unsupported url" in lowered_message or "not a valid url" in lowered_message:
        return "This URL is not supported. Check that you copied a complete media URL."
    if "private" in lowered_message or "sign in" in lowered_message or "login" in lowered_message:
        return "This media is private or requires sign-in, so its formats cannot be listed."
    if operation == "download":
        return "The selected media format could not be downloaded. Check the URL and try again."
    return "The media service could not provide formats. Check the URL and try again."


def list_formats(url: str):
    """List downloadable audio/video formats for a URL."""
    options: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "cookiesfrombrowser": ("chrome",),
    }
    info: dict[str, Any] | None = None
    last_error: Exception | None = None
    anonymous_options = {key: value for key, value in options.items() if key != "cookiesfrombrowser"}
    insecure_options = {**anonymous_options, "nocheckcertificate": True}
    for extractor_options in (options, anonymous_options, insecure_options):
        try:
            with yt_dlp.YoutubeDL(cast(Any, extractor_options)) as downloader:
                info = cast(dict[str, Any], downloader.extract_info(url, download=False))
            break
        except Exception as error:
            last_error = error
            continue
    if info is None:
        raise FormatListingError(describe_media_error(last_error or RuntimeError()))

    audio_formats = []
    video_formats = []
    for source_format in info.get("formats", []):
        format_id = source_format.get("format_id")
        if not format_id:
            continue

        format_details = {
            "format_id": format_id,
            "extn": source_format.get("ext", ""),
            "filesize": source_format.get("filesize") or source_format.get("filesize_approx") or "",
        }
        video_codec = source_format.get("vcodec")
        audio_codec = source_format.get("acodec")
        if video_codec == "none" and audio_codec not in (None, "none"):
            format_details["quality"] = source_format.get("abr") or ""
            audio_formats.append(format_details)
        elif video_codec not in (None, "none", "images"):
            format_details["resolution"] = source_format.get("resolution") or ""
            video_formats.append(format_details)

    if not audio_formats and not video_formats:
        raise FormatListingError(
            "The URL was reached, but it returned no downloadable audio or video formats. "
            "It may be private, restricted, or unavailable."
        )

    return audio_formats, video_formats


def clean_filename(filename: str, replacement: str = "_") -> str:
    invalid_chars_pattern = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars_pattern, replacement, filename).strip()


def identify_source(url: str) -> str:
    if re.search(r"youtube\.com|youtu\.be", url):
        return "youtube"
    if re.search(r"facebook\.com", url):
        return "facebook"
    if re.search(r"tiktok\.com", url):
        return "tiktok"
    if re.search(r"instagram\.com", url):
        return "instagram"
    return "other"


def download_youtube_media(
    url: str,
    format_id: str | None = None,
    output_path: str = "na",
):
    """Download a YouTube or similar media URL in the selected format."""
    ffmpeg_location = str(get_ffmpeg_dir())
    current_directory = os.getcwd()

    output_path = Path(output_path) if output_path != "na" else Path(current_directory)
    output_path = output_path / "downloaded_media" if output_path.is_dir() else output_path
    output_path_wo_extn = str(output_path.with_suffix(""))

    if os.path.isdir(output_path_wo_extn):
        outputtmpl = rf"{output_path_wo_extn}\%(id)s.%(ext)s"
    else:
        outputtmpl = rf"{output_path_wo_extn}.%(ext)s"

    ydl_opts = {
        "format": format_id or "bestvideo+bestaudio/best",
        "outtmpl": outputtmpl,
        "ffmpeg_location": ffmpeg_location,
        "noplaylist": True,
        "subtitleslangs": ["en"],
        "writesubtitles": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return str(output_path)


def main():
    print("YouTube/media download utility")


if __name__ == "__main__":
    main()
