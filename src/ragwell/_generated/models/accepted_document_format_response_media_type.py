from enum import StrEnum


class AcceptedDocumentFormatResponseMediaType(StrEnum):
    APPLICATIONPDF = "application/pdf"
    TEXTMARKDOWN = "text/markdown"
    TEXTPLAIN = "text/plain"

    def __str__(self) -> str:
        return str(self.value)
