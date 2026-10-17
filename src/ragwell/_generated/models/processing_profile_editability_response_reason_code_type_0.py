from enum import StrEnum


class ProcessingProfileEditabilityResponseReasonCodeType0(StrEnum):
    DOCUMENTS_PRESENT = "documents_present"
    INSUFFICIENT_PERMISSION = "insufficient_permission"

    def __str__(self) -> str:
        return str(self.value)
