from enum import StrEnum


class UploadState(StrEnum):
    EXPIRED = "expired"
    FINALIZED = "finalized"
    PENDING = "pending"
    REJECTED = "rejected"
    UPLOADED = "uploaded"

    def __str__(self) -> str:
        return str(self.value)
