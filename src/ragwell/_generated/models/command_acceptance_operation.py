from enum import Enum


class CommandAcceptanceOperation(str, Enum):
    DELETION_RETRY = "deletion.retry"
    DOCUMENT_METADATA_REPLACE = "document.metadata.replace"
    EXPORT_CREATE = "export.create"
    JOB_CANCEL = "job.cancel"
    JOB_RETRY = "job.retry"

    def __str__(self) -> str:
        return str(self.value)
