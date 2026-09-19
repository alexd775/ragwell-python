from enum import Enum


class DocumentVersionState(str, Enum):
    INDEXED = "indexed"
    QUARANTINED = "quarantined"
    REJECTED = "rejected"
    VALIDATED = "validated"

    def __str__(self) -> str:
        return str(self.value)
