from enum import Enum


class DocumentState(str, Enum):
    DELETED = "deleted"
    DELETION_PENDING = "deletion_pending"
    FAILED = "failed"
    QUARANTINED = "quarantined"
    READY = "ready"

    def __str__(self) -> str:
        return str(self.value)
