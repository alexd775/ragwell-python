from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.source_coordinate_kind import SourceCoordinateKind

if TYPE_CHECKING:
    from ..models.chunk_part import ChunkPart
    from ..models.embedding_serialization import EmbeddingSerialization


T = TypeVar("T", bound="DocumentChunkInfo")


@_attrs_define
class DocumentChunkInfo:
    character_count: int
    content: str
    coordinate_kind: SourceCoordinateKind
    document_version_id: UUID
    embedding_available: bool
    embedding_serialization: EmbeddingSerialization
    end_line: int | None
    end_offset: int
    estimated_tokens: int
    generation_id: UUID
    id: UUID
    ordinal: int
    page_number: int | None
    parts: list[ChunkPart]
    representation_version: str
    source_id: UUID
    source_ordinal: int
    start_line: int | None
    start_offset: int
    tokenizer_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        character_count = self.character_count

        content = self.content

        coordinate_kind = self.coordinate_kind.value

        document_version_id = str(self.document_version_id)

        embedding_available = self.embedding_available

        embedding_serialization = self.embedding_serialization.to_dict()

        end_line: int | None
        end_line = self.end_line

        end_offset = self.end_offset

        estimated_tokens = self.estimated_tokens

        generation_id = str(self.generation_id)

        id = str(self.id)

        ordinal = self.ordinal

        page_number: int | None
        page_number = self.page_number

        parts = []
        for parts_item_data in self.parts:
            parts_item = parts_item_data.to_dict()
            parts.append(parts_item)

        representation_version = self.representation_version

        source_id = str(self.source_id)

        source_ordinal = self.source_ordinal

        start_line: int | None
        start_line = self.start_line

        start_offset = self.start_offset

        tokenizer_id = self.tokenizer_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "character_count": character_count,
                "content": content,
                "coordinate_kind": coordinate_kind,
                "document_version_id": document_version_id,
                "embedding_available": embedding_available,
                "embedding_serialization": embedding_serialization,
                "end_line": end_line,
                "end_offset": end_offset,
                "estimated_tokens": estimated_tokens,
                "generation_id": generation_id,
                "id": id,
                "ordinal": ordinal,
                "page_number": page_number,
                "parts": parts,
                "representation_version": representation_version,
                "source_id": source_id,
                "source_ordinal": source_ordinal,
                "start_line": start_line,
                "start_offset": start_offset,
                "tokenizer_id": tokenizer_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chunk_part import ChunkPart
        from ..models.embedding_serialization import EmbeddingSerialization

        d = dict(src_dict)
        character_count = d.pop("character_count")

        content = d.pop("content")

        coordinate_kind = SourceCoordinateKind(d.pop("coordinate_kind"))

        document_version_id = UUID(d.pop("document_version_id"))

        embedding_available = d.pop("embedding_available")

        embedding_serialization = EmbeddingSerialization.from_dict(
            d.pop("embedding_serialization")
        )

        def _parse_end_line(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        end_line = _parse_end_line(d.pop("end_line"))

        end_offset = d.pop("end_offset")

        estimated_tokens = d.pop("estimated_tokens")

        generation_id = UUID(d.pop("generation_id"))

        id = UUID(d.pop("id"))

        ordinal = d.pop("ordinal")

        def _parse_page_number(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        page_number = _parse_page_number(d.pop("page_number"))

        parts = []
        _parts = d.pop("parts")
        for parts_item_data in _parts:
            parts_item = ChunkPart.from_dict(parts_item_data)

            parts.append(parts_item)

        representation_version = d.pop("representation_version")

        source_id = UUID(d.pop("source_id"))

        source_ordinal = d.pop("source_ordinal")

        def _parse_start_line(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        start_line = _parse_start_line(d.pop("start_line"))

        start_offset = d.pop("start_offset")

        tokenizer_id = d.pop("tokenizer_id")

        document_chunk_info = cls(
            character_count=character_count,
            content=content,
            coordinate_kind=coordinate_kind,
            document_version_id=document_version_id,
            embedding_available=embedding_available,
            embedding_serialization=embedding_serialization,
            end_line=end_line,
            end_offset=end_offset,
            estimated_tokens=estimated_tokens,
            generation_id=generation_id,
            id=id,
            ordinal=ordinal,
            page_number=page_number,
            parts=parts,
            representation_version=representation_version,
            source_id=source_id,
            source_ordinal=source_ordinal,
            start_line=start_line,
            start_offset=start_offset,
            tokenizer_id=tokenizer_id,
        )

        document_chunk_info.additional_properties = d
        return document_chunk_info

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
