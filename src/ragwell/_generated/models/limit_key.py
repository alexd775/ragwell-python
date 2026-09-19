from enum import Enum


class LimitKey(str, Enum):
    EMBEDDING_INPUT_TOKENS = "embedding_input_tokens"
    INDEXED_PAGES = "indexed_pages"
    PROJECTS = "projects"
    RETAINED_DOCUMENTS = "retained_documents"
    RETAINED_SOURCE_BYTES = "retained_source_bytes"
    SUCCESSFUL_SEARCHES = "successful_searches"

    def __str__(self) -> str:
        return str(self.value)
