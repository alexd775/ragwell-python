from enum import Enum


class EmbeddingConnectionResponseHealth(str, Enum):
    INTERVENTION_REQUIRED = "intervention_required"
    READY = "ready"
    TRANSIENT_FAILURE = "transient_failure"

    def __str__(self) -> str:
        return str(self.value)
