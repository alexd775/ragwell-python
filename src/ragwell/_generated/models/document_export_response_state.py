from enum import Enum


class DocumentExportResponseState(str, Enum):
    EXPIRED = "expired"
    FAILED = "failed"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"

    def __str__(self) -> str:
        return str(self.value)
