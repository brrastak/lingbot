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
    collocations: list[tuple[str, str]]
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

            # Extract collocations
            collocations = []
            for coll in soup.select("span.lex_ful_coll2s.w.l1"):
                src = coll.get_text(" ", strip=True)
                dst = coll.find_next("span", class_="lex_ful_coll2t").get_text(" ", strip=True)
                collocations.append((src, dst))

            # Extract fulltext examples
            examples = []
            for row in soup.select("table.fulltext tr.lex_ftx_sens"):
                src = row.select_one("span.lex_ftx_samp2s").get_text(" ", strip=True)
                dst = row.select_one("span.lex_ftx_samp2t").get_text(" ", strip=True)
                examples.append((src, dst))

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

        return TranslationResult(translations, collocations, examples)
