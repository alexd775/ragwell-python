from enum import Enum


class SourceCoordinateKind(str, Enum):
    PAGE = "page"
    TEXT = "text"

    def __str__(self) -> str:
        return str(self.value)
