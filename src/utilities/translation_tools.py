"""Text translation helpers."""

from __future__ import annotations

try:
    from googletrans import Translator as GoogleTranslator
except Exception:  # pragma: no cover - Python 3.13 compatibility guard
    GoogleTranslator = None

from translate import Translator


def google_translate_text(text, translator=None, source_language=None, target_language="en"):
    try:
        if GoogleTranslator is None:
            translator = Translator(to_lang=target_language)
            if source_language is not None:
                translator = Translator(from_lang=source_language, to_lang=target_language)
            return translator.translate(text)

        if translator is None:
            translator = GoogleTranslator()
        if source_language is None:
            translation = translator.translate(text, dest=target_language)
        else:
            translation = translator.translate(text, dest=target_language, src=source_language)
        return translation.text
    except Exception as exc:
        print(f"Translation error: {exc}")
        return None


def translate_text(text_chunk, translator):
    return translator.translate(text_chunk)


def translate_file(input_file, output_file, src_lang=None, tgt_lang="en", translatortype="google"):
    chunk_size = 500

    if translatortype == "google" and GoogleTranslator is not None:
        google_translator = GoogleTranslator()
    else:
        if src_lang is None:
            translator = Translator(to_lang=tgt_lang)
        else:
            translator = Translator(from_lang=src_lang, to_lang=tgt_lang)

    with open(input_file, "r", encoding="utf-8") as file:
        input_text = file.read()

    input_chunks = [input_text[i:i + chunk_size] for i in range(0, len(input_text), chunk_size)]
    translated_chunks = []

    for chunk in input_chunks:
        if translatortype == "google" and GoogleTranslator is not None:
            translated_chunk = google_translate_text(chunk, google_translator, src_lang, tgt_lang)
        else:
            translated_chunk = translate_text(chunk, translator)
        translated_chunks.append(translated_chunk)

    translated_text = "".join(translated_chunks)
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(translated_text)

    return output_file


def main():
    print("Translation utility")


if __name__ == "__main__":
    main()
