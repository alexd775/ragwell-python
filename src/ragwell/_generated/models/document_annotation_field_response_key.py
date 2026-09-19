from enum import Enum


class DocumentAnnotationFieldResponseKey(str, Enum):
    AUTHOR = "author"
    CATEGORY = "category"
    LANGUAGE = "language"
    SOURCE = "source"

    def __str__(self) -> str:
        return str(self.value)
