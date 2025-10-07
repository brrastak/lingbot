import httpx
import logging
from bs4 import BeautifulSoup
from dataclasses import dataclass
from enum import Enum
from urllib.parse import quote


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class Dictionary(Enum):
    RU_SK = ("RU-SK", "🇷🇺", "https://slovniky.lingea.sk/rusko-slovensky/")
    EN_SK = ("EN-SK", "🇬🇧", "https://slovniky.lingea.sk/anglicko-slovensky/")
    UA_SK = ("UA-SK", "🇺🇦", "https://slovniky.lingea.sk/ukrajinsko-slovensky/")

    def __init__(self, label: str, flag: str, url: str):
        self._label = label
        self._flag = flag
        self._url = url

    @property
    def label(self) -> str:
        return self._label

    @property
    def flag(self) -> str:
        return self._flag

    @property
    def url(self) -> str:
        return self._url
    
    @classmethod
    def default(cls) -> "Dictionary":
        return cls.EN_SK


@dataclass
class Translation:
    translations: list[str]
    examples: list[tuple[str, str]]


async def get(word: str, dict: Dictionary) -> Translation | None:
    url = f"{dict.url}{quote(word)}"
    
    try:
        # Request translation
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            # Check request status
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "lxml")

        # Extract main translations
        translations = [
            span.get_text(" ", strip=True) 
            for span in soup.select("span.lex_ful_tran.w.l2")
        ]

        examples = []
        # All wrapper spans that hold a source/translation pair
        for wrapper in soup.select("span[class$='2']"):  # matches lex_ful_coll2, lex_ful_samp2, lex_ful_idis2
            src_span = wrapper.find(
                lambda tag: tag.name == "span"
                and tag.get("class")
                and any(c.endswith("2s") for c in tag["class"])
            )
            dst_span = wrapper.find(
                lambda tag: tag.name == "span"
                and tag.get("class")
                and any(c.endswith("2t") for c in tag["class"])
            )
            
            if src_span:
                src = src_span.get_text(" ", strip=True)
                dst = dst_span.get_text(" ", strip=True) if dst_span else ""
                examples.append((src, dst))

    except Exception as e:
        logging.exception(f"Failed to fetch translation for \"%s\": %s", word, e)
        return None

    return Translation(translations, examples)
