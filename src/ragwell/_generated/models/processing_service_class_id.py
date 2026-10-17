from enum import StrEnum


class ProcessingServiceClassId(StrEnum):
    ACCELERATED_V1 = "accelerated-v1"
    SHARED_V1 = "shared-v1"
    STANDARD_V1 = "standard-v1"

    def __str__(self) -> str:
        return str(self.value)
