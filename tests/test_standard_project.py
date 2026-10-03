import importlib


def test_package_modules_exist():
    modules = [
        "utilities.audio_tools",
        "utilities.youtube_tools",
        "utilities.translation_tools",
        "utilities.transcription_tools",
        "utilities.html_cleaner",
        "utilities.cli",
    ]

    for name in modules:
        mod = importlib.import_module(name)
        assert mod is not None


def test_expected_functions_exist():
    from utilities.audio_tools import convert_audio
    from utilities.youtube_tools import download_youtube_media
    from utilities.translation_tools import translate_text, translate_file
    from utilities.transcription_tools import transcribe_audio
    from utilities.html_cleaner import replace_in_files_wrapper

    assert callable(convert_audio)
    assert callable(download_youtube_media)
    assert callable(translate_text)
    assert callable(translate_file)
    assert callable(transcribe_audio)
    assert callable(replace_in_files_wrapper)
