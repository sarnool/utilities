# Utilities Toolkit

This project contains a standard Python package for the core utilities you kept:

1. Audio converter
2. YouTube downloader
3. Language translator
4. Audio transcriber

The project is structured as a proper Python package and is installed via `pip install -e .`.

---

## Quick start

Use Python 3.11 for this project.

```powershell
cd c:\workspace\Utilities
python -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
python -m pip install -e .
```

Once installed, you can use the package from Python or the CLI entry points, for example:

```powershell
python -c "import utilities; print(utilities.convert_audio)"
convert-audio --help
download-youtube --help
translate-text --help
transcribe-audio --help
```

---

## Project structure

```text
Utilities/
├── README.md
├── pyproject.toml
├── requirements.txt
├── src/
│   └── utilities/
│       ├── __init__.py
│       ├── audio_tools.py
│       ├── youtube_tools.py
│       ├── translation_tools.py
│       ├── transcription_tools.py
│       ├── html_cleaner.py
│       └── cli.py
├── tests/
│   └── test_standard_project.py
└── .venv/
```

---

## Included functionality

### Audio converter
- Converts audio files to different formats
- Useful for preparing audio before transcription or playback

### YouTube downloader
- Lists available media formats
- Downloads video or audio from supported URLs
- Supports output paths and format selection

### Language translator
- Translates text or text files into another language
- Supports file-based translation workflows

### Audio transcriber
- Uses Whisper to transcribe audio to text
- Saves transcripts in common output formats

---

## Notes

- This project is now organized as a standard Python package rather than a loose set of scripts.
- The package entry points are installed through `pyproject.toml`.
- Some media/transcription features may require FFmpeg and a compatible runtime environment.
- If you want to avoid the package install flow, `requirements.txt` can still be used as a fallback, but the preferred method is `python -m pip install -e .`.
