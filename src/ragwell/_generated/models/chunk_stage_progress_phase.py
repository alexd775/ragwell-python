from enum import Enum


class ChunkStageProgressPhase(str, Enum):
    ANALYSIS = "analysis"
    ASSEMBLY = "assembly"

    def __str__(self) -> str:
        return str(self.value)
