from enum import StrEnum


class RerankMetadataProvider(StrEnum):
    OPENROUTER = "openrouter"
    TYPESAFE = "typesafe"
    VERCEL = "vercel"

    def __str__(self) -> str:
        return str(self.value)
