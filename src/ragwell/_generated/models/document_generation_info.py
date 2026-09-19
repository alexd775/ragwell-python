from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.index_generation_status import IndexGenerationStatus

T = TypeVar("T", bound="DocumentGenerationInfo")


@_attrs_define
class DocumentGenerationInfo:
    activated_at: datetime.datetime | None
    chunk_count: int | None
    created_at: datetime.datetime
    document_version_id: UUID
    generation_number: int
    id: UUID
    indexed_page_units: int
    inspectable: bool
    profile_id: str
    source_character_count: int | None
    source_count: int
    source_estimated_tokens: int | None
    source_line_count: int | None
    source_page_count: int | None
    source_tokenizer_id: None | str
    status: IndexGenerationStatus
    validated_at: datetime.datetime | None
    vector_count: int | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        activated_at: None | str
        if isinstance(self.activated_at, datetime.datetime):
            activated_at = self.activated_at.isoformat()
        else:
            activated_at = self.activated_at

        chunk_count: int | None
        chunk_count = self.chunk_count

        created_at = self.created_at.isoformat()

        document_version_id = str(self.document_version_id)

        generation_number = self.generation_number

        id = str(self.id)

        indexed_page_units = self.indexed_page_units

        inspectable = self.inspectable

        profile_id = self.profile_id

        source_character_count: int | None
        source_character_count = self.source_character_count

        source_count = self.source_count

        source_estimated_tokens: int | None
        source_estimated_tokens = self.source_estimated_tokens

        source_line_count: int | None
        source_line_count = self.source_line_count

        source_page_count: int | None
        source_page_count = self.source_page_count

        source_tokenizer_id: None | str
        source_tokenizer_id = self.source_tokenizer_id

        status = self.status.value

        validated_at: None | str
        if isinstance(self.validated_at, datetime.datetime):
            validated_at = self.validated_at.isoformat()
        else:
            validated_at = self.validated_at

        vector_count: int | None
        vector_count = self.vector_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "activated_at": activated_at,
                "chunk_count": chunk_count,
                "created_at": created_at,
                "document_version_id": document_version_id,
                "generation_number": generation_number,
                "id": id,
                "indexed_page_units": indexed_page_units,
                "inspectable": inspectable,
                "profile_id": profile_id,
                "source_character_count": source_character_count,
                "source_count": source_count,
                "source_estimated_tokens": source_estimated_tokens,
                "source_line_count": source_line_count,
                "source_page_count": source_page_count,
                "source_tokenizer_id": source_tokenizer_id,
                "status": status,
                "validated_at": validated_at,
                "vector_count": vector_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_activated_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                activated_at_type_0 = datetime.datetime.fromisoformat(data)

                return activated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        activated_at = _parse_activated_at(d.pop("activated_at"))

        def _parse_chunk_count(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        chunk_count = _parse_chunk_count(d.pop("chunk_count"))

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        document_version_id = UUID(d.pop("document_version_id"))

        generation_number = d.pop("generation_number")

        id = UUID(d.pop("id"))

        indexed_page_units = d.pop("indexed_page_units")

        inspectable = d.pop("inspectable")

        profile_id = d.pop("profile_id")

        def _parse_source_character_count(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        source_character_count = _parse_source_character_count(
            d.pop("source_character_count")
        )

        source_count = d.pop("source_count")

        def _parse_source_estimated_tokens(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        source_estimated_tokens = _parse_source_estimated_tokens(
            d.pop("source_estimated_tokens")
        )

        def _parse_source_line_count(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        source_line_count = _parse_source_line_count(d.pop("source_line_count"))

        def _parse_source_page_count(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        source_page_count = _parse_source_page_count(d.pop("source_page_count"))

        def _parse_source_tokenizer_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        source_tokenizer_id = _parse_source_tokenizer_id(d.pop("source_tokenizer_id"))

        status = IndexGenerationStatus(d.pop("status"))

        def _parse_validated_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                validated_at_type_0 = datetime.datetime.fromisoformat(data)

                return validated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        validated_at = _parse_validated_at(d.pop("validated_at"))

        def _parse_vector_count(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        vector_count = _parse_vector_count(d.pop("vector_count"))

        document_generation_info = cls(
            activated_at=activated_at,
            chunk_count=chunk_count,
            created_at=created_at,
            document_version_id=document_version_id,
            generation_number=generation_number,
            id=id,
            indexed_page_units=indexed_page_units,
            inspectable=inspectable,
            profile_id=profile_id,
            source_character_count=source_character_count,
            source_count=source_count,
            source_estimated_tokens=source_estimated_tokens,
            source_line_count=source_line_count,
            source_page_count=source_page_count,
            source_tokenizer_id=source_tokenizer_id,
            status=status,
            validated_at=validated_at,
            vector_count=vector_count,
        )

        document_generation_info.additional_properties = d
        return document_generation_info

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
