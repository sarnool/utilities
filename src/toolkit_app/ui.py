"""Local browser interface for the utilities toolkit."""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st


st.set_page_config(page_title="Utilities Toolkit", page_icon="🎛️", layout="wide")
st.markdown(
    """
    <style>
    :root {
        color-scheme: light;
        --ink: #202c2b;
        --muted: #64716e;
        --paper: #f5f6f1;
        --line: #dce2dc;
        --accent: #c24830;
        --accent-soft: #f3e1d9;
        --green: #1d7565;
    }
    [data-testid="stAppViewContainer"] { background: var(--paper); color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] { max-width: 1120px; padding-top: 2.4rem; }
    h1, h2, h3 { color: var(--ink); letter-spacing: 0; }
    h1 { font-size: 2.25rem; font-weight: 700; }
    [data-baseweb="tab-list"] { gap: .35rem; border-bottom: 1px solid var(--line); }
    [data-baseweb="tab"] { color: var(--muted); padding: .8rem 1rem; }
    [aria-selected="true"][data-baseweb="tab"] { color: var(--accent); }
    [data-testid="stFileUploader"] section { background: #fbfcf9; border-color: var(--line); }
    [data-testid="stDownloadButton"] button { border-color: var(--green); color: var(--green); }
    .tool-caption { color: var(--muted); margin: -.5rem 0 1.2rem; }
    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] { padding: 1.2rem 1rem; }
        h1 { font-size: 1.8rem; }
        [data-baseweb="tab"] { padding: .65rem .45rem; font-size: .86rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _save_upload(uploaded_file, directory: Path) -> Path:
    input_path = directory / Path(uploaded_file.name).name
    input_path.write_bytes(uploaded_file.getvalue())
    return input_path


def _set_results(key: str, paths: list[Path]) -> None:
    st.session_state[key] = [
        {"name": path.name, "data": path.read_bytes()} for path in paths
    ]


def _show_results(key: str) -> None:
    for index, result in enumerate(st.session_state.get(key, [])):
        st.download_button(
            f"Download {result['name']}",
            data=result["data"],
            file_name=result["name"],
            key=f"{key}-{index}-{result['name']}",
            use_container_width=True,
        )


def _convert_audio_tab() -> None:
    st.subheader("Convert audio")
    st.markdown('<p class="tool-caption">Choose a source file and output format.</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Audio file",
        type=["aac", "flac", "m4a", "mp3", "ogg", "wav", "wma"],
        key="convert-upload",
    )
    output_format = st.selectbox("Output format", ["mp3", "wav", "m4a", "flac", "ogg"])
    if st.button("Convert audio", type="primary", disabled=uploaded is None):
        try:
            from utilities.audio_tools import convert_audio

            with tempfile.TemporaryDirectory() as temp_dir:
                directory = Path(temp_dir)
                input_path = _save_upload(uploaded, directory)
                output_path = directory / f"converted.{output_format}"
                with st.spinner("Converting audio..."):
                    result_path = Path(convert_audio(str(input_path), str(output_path), output_format))
                _set_results("convert-results", [result_path])
            st.success("Conversion complete.")
        except Exception as exc:
            st.error(f"Conversion failed: {exc}")
    _show_results("convert-results")


def _download_media(url: str, audio_only: bool, output_format: str) -> list[Path]:
    import yt_dlp
    from utilities.ffmpeg_config import get_ffmpeg_dir

    with tempfile.TemporaryDirectory() as temp_dir:
        directory = Path(temp_dir)
        options = {
            "format": "bestaudio/best" if audio_only else "bestvideo+bestaudio/best",
            "outtmpl": str(directory / "%(title).160B [%(id)s].%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "ffmpeg_location": str(get_ffmpeg_dir()),
        }
        if audio_only:
            options["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": output_format,
            }]
        else:
            options["merge_output_format"] = output_format

        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.download([url])
        outputs = [path for path in directory.iterdir() if path.is_file()]
        if not outputs:
            raise RuntimeError("The downloader finished without creating an output file.")
        results = [{"name": path.name, "data": path.read_bytes()} for path in outputs]
        st.session_state["download-results"] = results
    return outputs


def _youtube_tab() -> None:
    st.subheader("Download media")
    st.markdown('<p class="tool-caption">Download one video or extract its audio.</p>', unsafe_allow_html=True)
    url = st.text_input("Media URL", placeholder="https://...")
    media_type = st.radio("Download as", ["Audio", "Video"], horizontal=True)
    audio_only = media_type == "Audio"
    output_format = st.selectbox(
        "Output format",
        ["mp3", "wav", "m4a"] if audio_only else ["mp4", "mkv", "webm"],
        key="download-format",
    )
    if st.button("Download media", type="primary", disabled=not url.strip()):
        try:
            with st.spinner("Downloading media..."):
                _download_media(url.strip(), audio_only, output_format)
            st.success("Download complete.")
        except Exception as exc:
            st.error(f"Download failed: {exc}. Check FFMPEG_DIR in the project-root .env file.")
    _show_results("download-results")


def _translate_tab() -> None:
    st.subheader("Translate a text file")
    st.markdown('<p class="tool-caption">Translate a UTF-8 text file and download the result.</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Text file", type=["txt"], key="translate-upload")
    source, target = st.columns(2)
    source_language = source.text_input("Source language", placeholder="Auto-detect")
    target_language = target.text_input("Target language", value="en")
    if st.button("Translate file", type="primary", disabled=uploaded is None):
        try:
            from utilities.translation_tools import translate_file

            with tempfile.TemporaryDirectory() as temp_dir:
                directory = Path(temp_dir)
                input_path = _save_upload(uploaded, directory)
                output_path = directory / f"{input_path.stem}_{target_language or 'translated'}.txt"
                with st.spinner("Translating text..."):
                    translate_file(
                        str(input_path),
                        str(output_path),
                        source_language.strip() or None,
                        target_language.strip() or "en",
                    )
                _set_results("translate-results", [output_path])
            st.success("Translation complete.")
        except Exception as exc:
            st.error(f"Translation failed: {exc}")
    _show_results("translate-results")


def _transcribe_tab() -> None:
    st.subheader("Transcribe audio")
    st.markdown('<p class="tool-caption">Run Whisper locally and save a transcript.</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Audio file",
        type=["aac", "flac", "m4a", "mp3", "ogg", "wav", "wma"],
        key="transcribe-upload",
    )
    left, middle, right = st.columns(3)
    language = left.text_input("Language", value="auto", help="Use auto to detect the spoken language.")
    model_size = middle.selectbox("Whisper model", ["tiny", "base", "small", "medium", "large"], index=3)
    output_format = right.selectbox("Transcript format", ["txt", "srt", "vtt", "json"])
    if st.button("Transcribe audio", type="primary", disabled=uploaded is None):
        try:
            from utilities.transcription_tools import transcribe_audio

            with tempfile.TemporaryDirectory() as temp_dir:
                directory = Path(temp_dir)
                input_path = _save_upload(uploaded, directory)
                output_dir = directory / "transcripts"
                output_dir.mkdir()
                with st.spinner(f"Transcribing with the {model_size} model..."):
                    transcribe_audio(
                        str(input_path),
                        input_language=language.strip() or "auto",
                        output_dir=str(output_dir),
                        output_format=output_format,
                        model_size=model_size,
                    )
                generated_files = sorted(path for path in output_dir.iterdir() if path.is_file())
                _set_results("transcribe-results", generated_files)
            st.success("Transcription complete.")
        except Exception as exc:
            st.error(f"Transcription failed: {exc}. Check FFMPEG_DIR in the project-root .env file.")
    _show_results("transcribe-results")


st.title("Utilities Toolkit")
st.markdown('<p class="tool-caption">Audio, media, and text tools in one workspace.</p>', unsafe_allow_html=True)
audio_tab, download_tab, translate_tab, transcribe_tab = st.tabs(
    ["Audio conversion", "Media download", "Translation", "Transcription"]
)

with audio_tab:
    _convert_audio_tab()
with download_tab:
    _youtube_tab()
with translate_tab:
    _translate_tab()
with transcribe_tab:
    _transcribe_tab()
