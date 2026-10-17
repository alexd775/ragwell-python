from enum import StrEnum


class EmbeddingConnectionNoticeResponseState(StrEnum):
    ACTIVE = "active"
    RECOVERED = "recovered"

    def __str__(self) -> str:
        return str(self.value)
