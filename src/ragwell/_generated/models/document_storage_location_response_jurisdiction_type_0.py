from enum import StrEnum


class DocumentStorageLocationResponseJurisdictionType0(StrEnum):
    EU = "eu"
    US = "us"

    def __str__(self) -> str:
        return str(self.value)
