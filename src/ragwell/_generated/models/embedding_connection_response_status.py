from enum import Enum


class EmbeddingConnectionResponseStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    VALIDATING = "validating"
    VALIDATION_FAILED = "validation_failed"

    def __str__(self) -> str:
        return str(self.value)
