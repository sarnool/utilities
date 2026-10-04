"""Utilities toolkit package."""

from .audio_tools import convert_audio
from .video_tools import convert_video
from .youtube_tools import download_youtube_media
from .html_cleaner import replace_in_files_wrapper

try:
    from .transcription_tools import transcribe_audio
except Exception:  # pragma: no cover - optional runtime dependency guard
    def transcribe_audio(*args, **kwargs):
        raise RuntimeError("Transcription support is unavailable because the optional transcription dependencies could not be imported.")

try:
    from .translation_tools import translate_text, translate_file
except Exception:  # pragma: no cover - optional dependency compatibility guard
    def translate_text(*args, **kwargs):
        raise RuntimeError("Translation support is unavailable because a compatible translator dependency could not be imported.")

    def translate_file(*args, **kwargs):
        raise RuntimeError("Translation support is unavailable because a compatible translator dependency could not be imported.")

__all__ = [
    "convert_audio",
    "convert_video",
    "download_youtube_media",
    "translate_text",
    "translate_file",
    "transcribe_audio",
    "replace_in_files_wrapper",
]
