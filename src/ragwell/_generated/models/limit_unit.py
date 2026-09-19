from enum import Enum


class LimitUnit(str, Enum):
    BYTES = "bytes"
    COUNT = "count"
    INPUT_TOKENS = "input_tokens"
    PAGES = "pages"
    SEARCH_UNITS = "search_units"

    def __str__(self) -> str:
        return str(self.value)
