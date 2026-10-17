from enum import StrEnum


class DocumentState(StrEnum):
    DELETED = "deleted"
    DELETION_PENDING = "deletion_pending"
    FAILED = "failed"
    QUARANTINED = "quarantined"
    READY = "ready"

    def __str__(self) -> str:
        return str(self.value)
