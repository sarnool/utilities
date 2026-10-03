"""YouTube/media download helpers."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import yt_dlp


FFMPEG_DIR = r"C:\workspace\ffmpeg\ffmpeg-7.1.1-essentials_build\bin"


def list_formats(url: str):
    """List downloadable audio/video formats for a URL."""
    command = ["yt-dlp", "--cookies-from-browser", "chrome", "--list-formats", url]
    try:
        output = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return [], []

    lines = output.stdout.strip().split("\n")
    start_collecting = False
    audio_formats = []
    video_formats = []
    header_line = ""

    for line in lines:
        if not start_collecting:
            if line[:10] == "----------":
                start_collecting = True
            else:
                header_line = line
            continue

        if "|" not in line:
            continue

        seg_1 = line.split("|")[0]
        extn = seg_1[header_line.find("EXT"):header_line.find("RESOLUTION")].strip()
        resolution = seg_1[header_line.find("RESOLUTION"):].strip()

        seg_2 = line.split("|")[1]
        filesize = seg_2[:header_line.split("|")[1].find("FILESIZE") + len("FILESIZE")].strip()

        seg_3 = line.split("|")[2]
        videoonly = seg_3[header_line.split("|")[2].find("ACODEC"):header_line.split("|")[2].find("ACODEC") + 13].strip()
        abr = seg_3[header_line.split("|")[2].find("ABR") - 1:header_line.split("|")[2].find("ABR") + 4].strip()
        moreinfo = seg_3[header_line.split("|")[2].find("MORE INFO"):].strip()
        if header_line.split("|")[2].find("MORE INFO") == -1:
            moreinfo = "tiktok"

        if resolution.lower() == "audio only":
            if len(abr.strip()) > 0:
                audio_formats.append({"extn": extn, "filesize": filesize, "quality": abr})
        elif videoonly.lower() == "video only" or resolution.find("x") > 0:
            if len(moreinfo.strip()) > 0:
                video_formats.append({"extn": extn, "filesize": filesize, "resolution": resolution})

        video_formats = [json.loads(x) for x in {json.dumps(v) for v in video_formats}]

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
    audio_only: bool = True,
    output_video_format: str = "mp4",
    output_audio_format: str = "wav",
    output_path: str = "na",
):
    """Download a YouTube or similar media URL to the desired format."""
    current_directory = os.getcwd()
    output_extn = output_audio_format if audio_only else output_video_format

    output_path = Path(output_path) if output_path != "na" else Path(current_directory)
    output_path = output_path / "downloaded_media" if output_path.is_dir() else output_path
    output_path_wo_extn = str(output_path.with_suffix(""))

    if os.path.isdir(output_path_wo_extn):
        outputtmpl = rf"{output_path_wo_extn}\%(id)s.%(ext)s"
    else:
        outputtmpl = rf"{output_path_wo_extn}.%(ext)s"

    audio_formats, video_formats = list_formats(url)
    url_source = identify_source(url)

    if audio_only:
        if url_source not in ("tiktok", "other"):
            print("\n".join([json.dumps(v) for v in audio_formats]))
            type_quality = input("Enter audio format and quality separated by comma (eg, webm, 104k): ")
            src_audio_format = type_quality.split(",")[0].strip()
            src_audio_quality = type_quality.split(",")[1].strip().replace("k", "")
        else:
            src_audio_format = "na"
            src_audio_quality = "na"

        ydl_opts = {
            "format": f"bestaudio[ext={src_audio_format}]/best[ext={src_audio_format}]/bestaudio",
            "outtmpl": outputtmpl,
            "ffmpeg_location": FFMPEG_DIR,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": output_audio_format,
                "preferredquality": src_audio_quality,
            }],
            "subtitleslangs": ["en"],
            "writesubtitles": True,
        }
    else:
        if url_source not in ("tiktok", "other"):
            print("\n".join([json.dumps(v) for v in video_formats]))
            type_quality = input("Enter video format and resolution separated by comma: ")
            src_video_format = type_quality.split(",")[0].strip()
            src_video_resolution = type_quality.split(",")[1].strip().replace("k", "")
        else:
            src_video_resolution = "na"
            src_video_format = "na"

        ydl_opts = {
            "format": f"bestvideo[height<={src_video_resolution}][ext={src_video_format}]/bestvideo+bestaudio",
            "outtmpl": outputtmpl,
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": output_video_format,
            }],
            "subtitleslangs": ["en"],
            "writesubtitles": True,
        }

    if "format" in ydl_opts:
        ydl_opts.pop("format")

    for postprocessor in ydl_opts.get("postprocessors", []):
        if "preferredquality" in postprocessor:
            postprocessor.pop("preferredquality")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return str(output_path)


def main():
    print("YouTube/media download utility")


if __name__ == "__main__":
    main()
