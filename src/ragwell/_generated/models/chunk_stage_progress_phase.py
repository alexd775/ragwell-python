from enum import StrEnum


class ChunkStageProgressPhase(StrEnum):
    ANALYSIS = "analysis"
    ASSEMBLY = "assembly"

    def __str__(self) -> str:
        return str(self.value)
