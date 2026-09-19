from enum import Enum


class AcceptedDocumentFormatResponseMediaType(str, Enum):
    APPLICATIONPDF = "application/pdf"
    TEXTMARKDOWN = "text/markdown"
    TEXTPLAIN = "text/plain"

    def __str__(self) -> str:
        return str(self.value)
