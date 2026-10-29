from enum import StrEnum


class DocumentStorageEditabilityResponseReasonCodeType0(StrEnum):
    DOCUMENTS_PRESENT = "documents_present"
    INSUFFICIENT_PERMISSION = "insufficient_permission"
    PENDING_WORK = "pending_work"

    def __str__(self) -> str:
        return str(self.value)
