from enum import StrEnum


class DocumentAnnotationFieldResponseKey(StrEnum):
    AUTHOR = "author"
    CATEGORY = "category"
    LANGUAGE = "language"
    SOURCE = "source"

    def __str__(self) -> str:
        return str(self.value)
