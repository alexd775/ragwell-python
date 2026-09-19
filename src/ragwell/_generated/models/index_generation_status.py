from enum import Enum


class IndexGenerationStatus(str, Enum):
    ACTIVE = "active"
    BUILDING = "building"
    SUPERSEDED = "superseded"

    def __str__(self) -> str:
        return str(self.value)
