import httpx
import logging
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import quote

from lingbot.translation.dictionary import Dictionary


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

        translation = parse(r.text)    

    except Exception as e:
        logging.exception(f"Failed to fetch translation for \"%s\": %s", word, e)
        return None

    return translation

def parse(source: str) -> Translation | None:
    soup = BeautifulSoup(source, "lxml")

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
    
    return Translation(translations, examples)
