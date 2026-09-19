from enum import Enum


class CreateUploadRequestDeclaredMediaType(str, Enum):
    APPLICATIONPDF = "application/pdf"
    TEXTMARKDOWN = "text/markdown"
    TEXTPLAIN = "text/plain"

    def __str__(self) -> str:
        return str(self.value)
