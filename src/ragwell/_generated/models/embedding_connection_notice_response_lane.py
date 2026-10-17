from enum import StrEnum


class EmbeddingConnectionNoticeResponseLane(StrEnum):
    INDEXING = "indexing"
    QUERY = "query"

    def __str__(self) -> str:
        return str(self.value)
