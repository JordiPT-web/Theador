"""Simple i18n utilities for English and Hebrew support."""

from typing import Literal

SUPPORTED_LANGS = {"en", "he"}

messages = {
    "greeting": {
        "en": "Hello",
        "he": "שלום",
    }
}


def translate(key: str, lang: str) -> str:
    if lang not in SUPPORTED_LANGS:
        lang = "en"
    return messages.get(key, {}).get(lang, key)


def direction(lang: str) -> Literal["ltr", "rtl"]:
    return "rtl" if lang == "he" else "ltr"
