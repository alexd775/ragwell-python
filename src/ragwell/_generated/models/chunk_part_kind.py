from enum import Enum


class ChunkPartKind(str, Enum):
    CONTEXT = "context"
    EVIDENCE = "evidence"
    SEPARATOR = "separator"

    def __str__(self) -> str:
        return str(self.value)
