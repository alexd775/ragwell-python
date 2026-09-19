from enum import Enum


class ProcessingProfileEditabilityResponseReasonCodeType0(str, Enum):
    DOCUMENTS_PRESENT = "documents_present"
    INSUFFICIENT_PERMISSION = "insufficient_permission"

    def __str__(self) -> str:
        return str(self.value)
