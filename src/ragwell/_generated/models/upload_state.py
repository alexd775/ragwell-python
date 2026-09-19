from enum import Enum


class UploadState(str, Enum):
    EXPIRED = "expired"
    FINALIZED = "finalized"
    PENDING = "pending"
    REJECTED = "rejected"
    UPLOADED = "uploaded"

    def __str__(self) -> str:
        return str(self.value)
