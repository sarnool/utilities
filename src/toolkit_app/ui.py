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
    audio_source = (uploaded.name, uploaded.size) if uploaded is not None else None
    if st.session_state.get("convert-source") != audio_source:
        st.session_state["convert-source"] = audio_source
        st.session_state.pop("convert-results", None)
    output_format = st.selectbox("Output format", ["mp3", "wav", "m4a", "flac", "ogg"])
    audio_action = st.empty()
    convert_audio_clicked = audio_action.button(
        "Convert audio",
        type="primary",
        disabled=uploaded is None,
    )
    if convert_audio_clicked:
        audio_action.button(
            "Converting...",
            icon=":material/hourglass_top:",
            disabled=True,
            key="converting-audio",
        )
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


def _convert_video_tab() -> None:
    st.subheader("Convert video")
    st.markdown('<p class="tool-caption">Choose a video file and output format.</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Video file",
        type=["avi", "flv", "m4v", "mkv", "mov", "mp4", "mpeg", "webm", "wmv"],
        key="convert-video-upload",
    )
    video_source = (uploaded.name, uploaded.size) if uploaded is not None else None
    if st.session_state.get("convert-video-source") != video_source:
        st.session_state["convert-video-source"] = video_source
        st.session_state.pop("convert-video-results", None)
    output_format = st.selectbox(
        "Output format",
        ["mp4", "mkv", "webm", "mov", "avi", "mp3", "wav", "m4a", "flac", "ogg"],
        key="convert-video-format",
    )
    video_action = st.empty()
    convert_video_clicked = video_action.button(
        "Convert video",
        type="primary",
        disabled=uploaded is None,
    )
    if convert_video_clicked:
        video_action.button(
            "Converting...",
            icon=":material/hourglass_top:",
            disabled=True,
            key="converting-video",
        )
        try:
            from utilities.video_tools import convert_video

            with tempfile.TemporaryDirectory() as temp_dir:
                directory = Path(temp_dir)
                input_path = _save_upload(uploaded, directory)
                output_path = directory / f"converted.{output_format}"
                with st.spinner("Converting video..."):
                    result_path = Path(convert_video(str(input_path), str(output_path), output_format))
                _set_results("convert-video-results", [result_path])
            st.success("Media conversion complete.")
        except Exception as exc:
            st.error(f"Media conversion failed: {exc}")
    _show_results("convert-video-results")


def _download_media(url: str, format_id: str) -> list[Path]:
    import yt_dlp
    from utilities.ffmpeg_config import get_ffmpeg_dir

    with tempfile.TemporaryDirectory() as temp_dir:
        directory = Path(temp_dir)
        options = {
            "format": format_id,
            "outtmpl": str(directory / "%(title).160B [%(id)s].%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "ffmpeg_location": str(get_ffmpeg_dir()),
        }

        with yt_dlp.YoutubeDL(options) as downloader:
            downloader.download([url])
        outputs = [path for path in directory.iterdir() if path.is_file()]
        if not outputs:
            raise RuntimeError("The downloader finished without creating an output file.")
        results = [{"name": path.name, "data": path.read_bytes()} for path in outputs]
        st.session_state["download-results"] = results
    return outputs


def _format_filesize(size: int | str) -> str:
    if not size:
        return "Size unavailable"
    size_in_bytes = int(size)
    for unit in ("B", "KB", "MB", "GB"):
        if size_in_bytes < 1024 or unit == "GB":
            return f"{size_in_bytes:.0f} {unit}" if unit == "B" else f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return "Size unavailable"


def _youtube_tab() -> None:
    st.subheader("Download media")
    st.markdown('<p class="tool-caption">Choose one of the formats provided by the source.</p>', unsafe_allow_html=True)
    st.caption("Supports YouTube, Facebook, TikTok, Instagram, Twitter/X, Reddit, Vimeo, Twitch, SoundCloud, Dailymotion, and other yt-dlp-supported sites.")
    url_column, action_column = st.columns([5, 1])
    with url_column:
        url = st.text_input("Media URL", placeholder="https://...")
    current_url = url.strip()
    loaded_url = st.session_state.get("download-url", "")
    show_load_button = current_url != loaded_url
    if show_load_button:
        st.session_state.pop("download-formats", None)
        st.session_state.pop("download-results", None)
    load_formats = False
    action_slot = None
    if show_load_button:
        with action_column:
            st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
            action_slot = st.empty()
            load_formats = action_slot.button(
                "Download media",
                type="primary",
                use_container_width=True,
            )
    if load_formats:
        if not current_url:
            st.warning("Enter a media URL first.")
        else:
            assert action_slot is not None
            action_slot.button(
                "Loading formats...",
                icon=":material/hourglass_top:",
                disabled=True,
                key="loading-media-formats",
                use_container_width=True,
            )
            try:
                from utilities.youtube_tools import describe_media_error, list_formats

                with st.spinner("Loading available formats..."):
                    audio_formats, video_formats = list_formats(current_url)
                formats = [
                    {**item, "kind": "Audio"} for item in audio_formats
                ] + [
                    {**item, "kind": "Video"} for item in video_formats
                ]
                st.session_state["show-unknown-size-formats"] = not any(
                    item.get("filesize") for item in formats
                )
                st.session_state["download-url"] = current_url
                st.session_state["download-formats"] = formats
                st.session_state.pop("download-results", None)
                action_slot.empty()
                st.success("Formats loaded. Select one to continue.")
            except Exception as exc:
                st.error(f"Could not load formats: {describe_media_error(exc)}")

    formats = st.session_state.get("download-formats", [])
    if formats:
        heading_column, filter_column = st.columns([3, 2])
        with heading_column:
            st.markdown("**Available formats**")
        with filter_column:
            show_unknown_size = st.checkbox(
                "Show size unavailable formats",
                value=False,
                key="show-unknown-size-formats",
            )
        visible_formats = [
            item for item in formats
            if show_unknown_size or item.get("filesize")
        ]
        if not visible_formats:
            st.info("No formats have a known file size. Streaming formats are shown instead.")
        download_actions = []
        for index, item in enumerate(visible_formats):
            details = [item["kind"], item.get("extn", "").upper()]
            if item["kind"] == "Audio":
                quality = item.get("quality")
                if quality:
                    details.append(f"{float(quality):.0f} kbps")
            else:
                resolution = item.get("resolution")
                if resolution:
                    details.append(resolution)
                details.append("video only")
            details.append(_format_filesize(item.get("filesize", "")))

            format_columns = st.columns([7, 1])
            with format_columns[0]:
                st.markdown(f"**{' · '.join(details)}**")
            with format_columns[1]:
                button_slot = st.empty()
                download_clicked = button_slot.button(
                    "Download",
                    icon=":material/download:",
                    help=f"Download {item['kind'].lower()} format {item['format_id']}",
                    key=f"download-format-{index}-{item['format_id']}",
                    use_container_width=True,
                )
                download_actions.append((button_slot, item, download_clicked))

        selected_download = next(
            ((button_slot, item) for button_slot, item, clicked in download_actions if clicked),
            None,
        )
        if selected_download:
            _, selected_item = selected_download
            for index, (button_slot, item, _) in enumerate(download_actions):
                button_slot.button(
                    "Downloading..." if item is selected_item else "Download",
                    icon=":material/downloading:" if item is selected_item else ":material/download:",
                    key=f"download-format-busy-{index}-{item['format_id']}",
                    disabled=True,
                    use_container_width=True,
                )
            try:
                with st.spinner(f"Downloading {selected_item['kind'].lower()} format..."):
                    _download_media(
                        st.session_state["download-url"],
                        selected_item["format_id"],
                    )
                st.success("Download complete.")
            except Exception as exc:
                from utilities.youtube_tools import describe_media_error

                st.error(f"Download failed: {describe_media_error(exc, operation='download')}")
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
audio_tab, video_tab, download_tab, translate_tab, transcribe_tab = st.tabs(
    ["Audio conversion", "Video conversion", "Media download", "Translation", "Transcription"]
)

with audio_tab:
    _convert_audio_tab()
with video_tab:
    _convert_video_tab()
with download_tab:
    _youtube_tab()
with translate_tab:
    _translate_tab()
with transcribe_tab:
    _transcribe_tab()
