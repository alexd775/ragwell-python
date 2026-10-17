from enum import StrEnum


class DocumentVersionState(StrEnum):
    INDEXED = "indexed"
    QUARANTINED = "quarantined"
    REJECTED = "rejected"
    VALIDATED = "validated"

    def __str__(self) -> str:
        return str(self.value)
