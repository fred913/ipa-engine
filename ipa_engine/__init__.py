import json
import string
from functools import lru_cache
from logging import Logger
from pathlib import Path
from typing import Callable

__all__ = ['LANGUAGES', "IPAEngine"]

LANGUAGES = {
    "en_US": "English (United States)",
    "eo": "Esperanto",
    "es_MX": "Spanish (Mexico)",
    "fa": "Persian",
    "fr_FR": "French (France)",
    "ja": "Japanese",
    "yue": "Cantonese",
    "zh_hans": "Chinese (Simplified)",
    "zh_hant": "Chinese (Traditional)"
}

SELF_PATH = Path(__file__)


class IPAEngine:

    def __init__(self,
                 languages: 'list[str] | None' = None,
                 logger: 'Logger | None' = None):
        self.logger = logger

        self._cache: dict[str, str] = {}  # dict[spelling: str, ipa: str]

        if languages is not None:
            for lang in languages:
                self._load(lang)
        else:
            # load en_US, ja, fr_FR, and zh_hans by default
            for lang in ['en_US', 'fr_FR', 'es_MX', 'zh_hans']:
                self._load(lang)

    def _load(self, lang: str):
        if lang in list(map(lambda x: x.lower(), LANGUAGES.keys())):
            lang = list(LANGUAGES.keys())[list(
                map(lambda x: x.lower(),
                    LANGUAGES.keys())).index(lang.lower())]

        if lang not in LANGUAGES:
            raise ValueError(f"Language {lang} is not supported.")

        with (SELF_PATH.parent / "ipa_resources" / f"{lang}.json").open(
                "r", encoding="utf-8") as f:
            self._cache.update(json.load(f))

    @lru_cache(65536, True)
    def _tokenize(self, sentence: str) -> list[str]:
        tokens = []
        for x in r"""!"#$%&()*+,-./:;<=>?@[\]^_`{|}~""":
            sentence = sentence.replace(x, "")
        for x in string.whitespace:
            if x != " ":
                sentence = sentence.replace(x, " ")
        sentence = sentence.lower().strip()
        while sentence:
            found = False
            # Try to match the longest possible word in the cache
            for i in range(len(sentence), 0, -1):
                word = sentence[:i]
                if word in self._cache:
                    tokens.append(word)
                    sentence = sentence[i:]  # Remove the matched word
                    found = True
                    break
            if not found:
                # If no match found, consume one character
                tokens.append(sentence[0])
                sentence = sentence[1:]
        return tokens

    def translate_ipa(
            self,
            sentence: str,
            preserve_unknown: 'Callable[[str], str] | bool' = False
    ) -> list[str]:
        tokens = self._tokenize(sentence)
        ipa_translations = []

        for token in tokens:
            if token in self._cache:
                ipa_possibilities: list[str] = list(
                    map(lambda x: str(x).strip().strip('/'),
                        self._cache[token].split(",")))
                ipa_translations.append(ipa_possibilities[0])
            elif token == " ":
                ipa_translations.append(" ")  # Keep spaces as they are
            else:
                # ipa_translations.append(f"[{token}]")  # Indicate missing words
                # logger.warning(
                #     f"Word '{token}' not found in the IPA dictionary.", )

                if preserve_unknown:
                    if callable(preserve_unknown):
                        ipa_translations.append(preserve_unknown(token))
                    else:
                        ipa_translations.append(token)
                else:
                    if self.logger:
                        self.logger.warning(
                            f"Word '{token}' not found in the IPA dictionary.")

        return ipa_translations
