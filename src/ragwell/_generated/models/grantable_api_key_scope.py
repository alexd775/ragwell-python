from enum import Enum


class GrantableApiKeyScope(str, Enum):
    DELETIONREAD = "deletion:read"
    DELETIONRETRY = "deletion:retry"
    DOCUMENTDELETE = "document:delete"
    DOCUMENTLIST = "document:list"
    DOCUMENTREAD = "document:read"
    DOCUMENTUPDATE = "document:update"
    DOCUMENTUPLOAD = "document:upload"
    JOBCANCEL = "job:cancel"
    JOBLIST = "job:list"
    JOBREAD = "job:read"
    JOBRETRY = "job:retry"
    PROJECTREAD = "project:read"
    RETRIEVALSEARCH = "retrieval:search"

    def __str__(self) -> str:
        return str(self.value)
