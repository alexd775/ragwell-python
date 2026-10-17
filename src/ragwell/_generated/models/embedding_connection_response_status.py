from enum import StrEnum


class EmbeddingConnectionResponseStatus(StrEnum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    VALIDATING = "validating"
    VALIDATION_FAILED = "validation_failed"

    def __str__(self) -> str:
        return str(self.value)
