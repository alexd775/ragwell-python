from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchFilters")


@_attrs_define
class SearchFilters:
    author_any: list[str] | Unset = UNSET
    category_any: list[str] | Unset = UNSET
    document_ids: list[UUID] | Unset = UNSET
    language_any: list[str] | Unset = UNSET
    source_any: list[str] | Unset = UNSET
    tags_all: list[str] | Unset = UNSET
    tags_any: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        author_any: list[str] | Unset = UNSET
        if not isinstance(self.author_any, Unset):
            author_any = self.author_any

        category_any: list[str] | Unset = UNSET
        if not isinstance(self.category_any, Unset):
            category_any = self.category_any

        document_ids: list[str] | Unset = UNSET
        if not isinstance(self.document_ids, Unset):
            document_ids = []
            for document_ids_item_data in self.document_ids:
                document_ids_item = str(document_ids_item_data)
                document_ids.append(document_ids_item)

        language_any: list[str] | Unset = UNSET
        if not isinstance(self.language_any, Unset):
            language_any = self.language_any

        source_any: list[str] | Unset = UNSET
        if not isinstance(self.source_any, Unset):
            source_any = self.source_any

        tags_all: list[str] | Unset = UNSET
        if not isinstance(self.tags_all, Unset):
            tags_all = self.tags_all

        tags_any: list[str] | Unset = UNSET
        if not isinstance(self.tags_any, Unset):
            tags_any = self.tags_any

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if author_any is not UNSET:
            field_dict["author_any"] = author_any
        if category_any is not UNSET:
            field_dict["category_any"] = category_any
        if document_ids is not UNSET:
            field_dict["document_ids"] = document_ids
        if language_any is not UNSET:
            field_dict["language_any"] = language_any
        if source_any is not UNSET:
            field_dict["source_any"] = source_any
        if tags_all is not UNSET:
            field_dict["tags_all"] = tags_all
        if tags_any is not UNSET:
            field_dict["tags_any"] = tags_any

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        author_any = cast(list[str], d.pop("author_any", UNSET))

        category_any = cast(list[str], d.pop("category_any", UNSET))

        _document_ids = d.pop("document_ids", UNSET)
        document_ids: list[UUID] | Unset = UNSET
        if _document_ids is not UNSET:
            document_ids = []
            for document_ids_item_data in _document_ids:
                document_ids_item = UUID(document_ids_item_data)

                document_ids.append(document_ids_item)

        language_any = cast(list[str], d.pop("language_any", UNSET))

        source_any = cast(list[str], d.pop("source_any", UNSET))

        tags_all = cast(list[str], d.pop("tags_all", UNSET))

        tags_any = cast(list[str], d.pop("tags_any", UNSET))

        search_filters = cls(
            author_any=author_any,
            category_any=category_any,
            document_ids=document_ids,
            language_any=language_any,
            source_any=source_any,
            tags_all=tags_all,
            tags_any=tags_any,
        )

        return search_filters
