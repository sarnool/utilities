"""Audio transcription helpers."""

from __future__ import annotations

import os
from pathlib import Path

from .ffmpeg_config import configure_ffmpeg_path

try:
    import torch
    import torchaudio
    import whisper
except Exception:  # pragma: no cover - optional dependency guard
    torch = None
    torchaudio = None
    whisper = None


def get_device():
    if torch is None:
        raise RuntimeError("Transcription support requires torch and whisper to be installed.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if str(device) == "cpu":
        try:
            torch.cuda.set_device(0)
            device = torch.device("cuda:0")
        except Exception:
            device = torch.device("cpu")
    return device


def transcribe_audio(
    input_path,
    input_language="auto",
    task="transcribe",
    output_dir="na",
    output_format="all",
    model_size="medium",
):
    """Transcribe an audio file using Whisper and save output to disk."""
    if whisper is None or torch is None:
        raise RuntimeError("Transcription support is unavailable because whisper/torch could not be imported.")

    configure_ffmpeg_path()
    device = get_device()

    if output_dir == "na":
        output_dir = Path(input_path).parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    model = whisper.load_model(model_size).to(device)

    if input_language == "auto":
        result = model.transcribe(audio=input_path, task=task)
    else:
        result = model.transcribe(audio=input_path, language=input_language, task=task)

    writer = whisper.utils.get_writer(output_format=output_format, output_dir=str(output_dir))
    writer(result, Path(input_path).stem, options=dict(
        highlight_words=False,
        max_line_count=None,
        max_line_width=None,
    ))

    return result


def main():
    print("Transcription utility")


if __name__ == "__main__":
    main()
