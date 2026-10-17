from enum import StrEnum


class ChunkPartKind(StrEnum):
    CONTEXT = "context"
    EVIDENCE = "evidence"
    SEPARATOR = "separator"

    def __str__(self) -> str:
        return str(self.value)
