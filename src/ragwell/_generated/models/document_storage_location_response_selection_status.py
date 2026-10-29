from enum import StrEnum


class DocumentStorageLocationResponseSelectionStatus(StrEnum):
    ACTIVE = "active"
    RETIRED = "retired"
    UNAVAILABLE = "unavailable"

    def __str__(self) -> str:
        return str(self.value)
