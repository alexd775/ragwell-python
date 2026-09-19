from enum import Enum


class EmbeddingConnectionNoticeResponseState(str, Enum):
    ACTIVE = "active"
    RECOVERED = "recovered"

    def __str__(self) -> str:
        return str(self.value)
