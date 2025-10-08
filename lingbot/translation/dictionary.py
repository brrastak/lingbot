from enum import Enum


# Label + flag + link to use for translation
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

# Return Dictionary value with corresponding label
def str_to_dict(label: str) -> Dictionary | None:
    for dict in Dictionary:
        if dict.label == label:
            return dict
    return None
