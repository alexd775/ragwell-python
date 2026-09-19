from enum import Enum


class IngestionStage(str, Enum):
    CHUNK = "chunk"
    COMPLETE = "complete"
    EMBED = "embed"
    EXTRACT = "extract"
    INDEX = "index"
    SCAN = "scan"

    def __str__(self) -> str:
        return str(self.value)
