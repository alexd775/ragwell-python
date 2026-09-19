from enum import Enum


class StructuralUnitKind(str, Enum):
    CODE = "code"
    FURNITURE = "furniture"
    HEADING = "heading"
    LIST = "list"
    PARAGRAPH = "paragraph"
    TABLE_ROW = "table_row"

    def __str__(self) -> str:
        return str(self.value)
