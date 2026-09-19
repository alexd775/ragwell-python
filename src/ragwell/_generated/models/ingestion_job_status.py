from enum import Enum


class IngestionJobStatus(str, Enum):
    CANCELLATION_REQUESTED = "cancellation_requested"
    CANCELLED = "cancelled"
    FAILED = "failed"
    QUEUED = "queued"
    RETRY_WAIT = "retry_wait"
    RUNNING = "running"
    SUCCEEDED = "succeeded"

    def __str__(self) -> str:
        return str(self.value)
