from enum import StrEnum


class DocumentDeletionState(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"
    RETRY_WAIT = "retry_wait"
    RUNNING = "running"

    def __str__(self) -> str:
        return str(self.value)
