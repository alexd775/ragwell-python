from enum import Enum


class AttemptStatus(str, Enum):
    CANCELLED = "cancelled"
    FAILED = "failed"
    RUNNING = "running"
    SUCCEEDED = "succeeded"

    def __str__(self) -> str:
        return str(self.value)
