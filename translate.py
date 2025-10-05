import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from enum import Enum
from urllib.parse import quote


class TranslationSource(Enum):
    RU_SK = ("RU-SK", "https://slovniky.lingea.sk/rusko-slovensky/")
    EN_SK = ("EN-SK", "https://slovniky.lingea.sk/anglicko-slovensky/")

    def __init__(self, label: str, url: str):
        self._label = label
        self._url = url

    @property
    def label(self) -> str:
        return self._label

    @property
    def url(self) -> str:
        return self._url


@dataclass
class TranslationResult:
    translations: list[str]
    examples: list[tuple[str, str]]


class Translation:
    def __init__(self, source: TranslationSource) -> None:
        self._source = source

    def get(self, word) -> TranslationResult | None:
        url = f"{self._source.url}{quote(word)}"
        
        try:
            # Request translation
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            # Check request status
            r.raise_for_status()
            # Parse the page
            soup = BeautifulSoup(r.text, "html.parser")

            # Extract main translations
            translations = [span.get_text(" ", strip=True) 
                            for span in soup.select("span.lex_ful_tran.w.l2")]

            examples = []
            # All wrapper spans that hold a source/translation pair
            for wrapper in soup.select("span[class$='2']"):  # matches lex_ful_coll2, lex_ful_samp2, lex_ful_idis2
                src_span = wrapper.find(lambda tag: tag.name == "span" and tag.get("class") and any(c.endswith("2s") for c in tag["class"]))
                dst_span = wrapper.find(lambda tag: tag.name == "span" and tag.get("class") and any(c.endswith("2t") for c in tag["class"]))
                
                if src_span:
                    src = src_span.get_text(" ", strip=True)
                    dst = dst_span.get_text(" ", strip=True) if dst_span else ""
                    examples.append((src, dst))

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

        return TranslationResult(translations, examples)
