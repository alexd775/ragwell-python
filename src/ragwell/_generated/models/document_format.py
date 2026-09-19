from enum import Enum


class DocumentFormat(str, Enum):
    MARKDOWN = "markdown"
    PDF = "pdf"
    PLAIN_TEXT = "plain_text"

    def __str__(self) -> str:
        return str(self.value)
