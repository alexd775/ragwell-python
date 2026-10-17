from enum import StrEnum


class SourceCoordinateKind(StrEnum):
    PAGE = "page"
    TEXT = "text"

    def __str__(self) -> str:
        return str(self.value)
