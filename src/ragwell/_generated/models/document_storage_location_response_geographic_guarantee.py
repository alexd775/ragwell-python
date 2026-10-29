from enum import StrEnum


class DocumentStorageLocationResponseGeographicGuarantee(StrEnum):
    JURISDICTION_RESTRICTED = "jurisdiction_restricted"
    UNSPECIFIED = "unspecified"

    def __str__(self) -> str:
        return str(self.value)
