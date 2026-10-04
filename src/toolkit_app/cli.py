"""Command-line entry points for the utilities toolkit."""

from __future__ import annotations

import argparse

from utilities.audio_tools import convert_audio
from utilities.youtube_tools import download_youtube_media

try:
    from utilities.translation_tools import translate_file
except Exception:  # pragma: no cover - optional dependency guard
    translate_file = None

try:
    from utilities.transcription_tools import transcribe_audio
except Exception:  # pragma: no cover - optional dependency guard
    transcribe_audio = None


def convert_audio_cli():
    parser = argparse.ArgumentParser(description="Convert audio to another format")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("--format", default="mp3")
    args = parser.parse_args()
    print(convert_audio(args.input_file, args.output_file, args.format))


def download_youtube_cli():
    parser = argparse.ArgumentParser(description="Download media from a URL")
    parser.add_argument("url")
    parser.add_argument("--format-id", default=None, help="yt-dlp format ID from the available formats")
    parser.add_argument("--output-path", default=".")
    args = parser.parse_args()
    print(download_youtube_media(args.url, format_id=args.format_id, output_path=args.output_path))


def translate_text_cli():
    if translate_file is None:
        raise RuntimeError("Translation support is unavailable because a compatible translator dependency could not be imported.")

    parser = argparse.ArgumentParser(description="Translate a file")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("--src-lang", default=None)
    parser.add_argument("--tgt-lang", default="en")
    args = parser.parse_args()
    print(translate_file(args.input_file, args.output_file, args.src_lang, args.tgt_lang))


def transcribe_audio_cli():
    if transcribe_audio is None:
        raise RuntimeError("Transcription support is unavailable because whisper/torch could not be imported.")

    parser = argparse.ArgumentParser(description="Transcribe audio using Whisper")
    parser.add_argument("input_path")
    parser.add_argument("--language", default="auto")
    parser.add_argument("--output-dir", default="na")
    parser.add_argument("--output-format", default="all")
    parser.add_argument("--model-size", default="medium")
    args = parser.parse_args()
    result = transcribe_audio(
        args.input_path,
        input_language=args.language,
        output_dir=args.output_dir,
        output_format=args.output_format,
        model_size=args.model_size,
    )
    print(result)


if __name__ == "__main__":
    convert_audio_cli()
