from enum import StrEnum


class DocumentStorageLocationResponseProvider(StrEnum):
    CLOUDFLARE_R2 = "cloudflare_r2"
    FILESYSTEM = "filesystem"

    def __str__(self) -> str:
        return str(self.value)
