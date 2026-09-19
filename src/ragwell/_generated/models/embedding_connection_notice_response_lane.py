from enum import Enum


class EmbeddingConnectionNoticeResponseLane(str, Enum):
    INDEXING = "indexing"
    QUERY = "query"

    def __str__(self) -> str:
        return str(self.value)
