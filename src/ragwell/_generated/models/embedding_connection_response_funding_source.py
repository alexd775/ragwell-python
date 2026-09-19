from enum import Enum


class EmbeddingConnectionResponseFundingSource(str, Enum):
    CUSTOMER = "customer"
    SYSTEM = "system"

    def __str__(self) -> str:
        return str(self.value)
