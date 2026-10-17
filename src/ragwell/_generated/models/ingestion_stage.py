from enum import StrEnum


class IngestionStage(StrEnum):
    CHUNK = "chunk"
    COMPLETE = "complete"
    EMBED = "embed"
    EXTRACT = "extract"
    INDEX = "index"
    SCAN = "scan"

    def __str__(self) -> str:
        return str(self.value)
