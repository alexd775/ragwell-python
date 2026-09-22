from enum import Enum


class RerankMetadataProvider(str, Enum):
    OPENROUTER = "openrouter"
    TYPESAFE = "typesafe"
    VERCEL = "vercel"

    def __str__(self) -> str:
        return str(self.value)
