from enum import StrEnum


class IndexGenerationStatus(StrEnum):
    ACTIVE = "active"
    BUILDING = "building"
    SUPERSEDED = "superseded"

    def __str__(self) -> str:
        return str(self.value)
