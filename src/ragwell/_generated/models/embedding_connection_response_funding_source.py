from enum import StrEnum


class EmbeddingConnectionResponseFundingSource(StrEnum):
    CUSTOMER = "customer"
    SYSTEM = "system"

    def __str__(self) -> str:
        return str(self.value)
