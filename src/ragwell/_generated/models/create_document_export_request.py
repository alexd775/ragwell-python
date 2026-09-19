from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateDocumentExportRequest")


@_attrs_define
class CreateDocumentExportRequest:
    generation_id: UUID
    include_embeddings: bool | Unset = False

    def to_dict(self) -> dict[str, Any]:
        generation_id = str(self.generation_id)

        include_embeddings = self.include_embeddings

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "generation_id": generation_id,
            }
        )
        if include_embeddings is not UNSET:
            field_dict["include_embeddings"] = include_embeddings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        generation_id = UUID(d.pop("generation_id"))

        include_embeddings = d.pop("include_embeddings", UNSET)

        create_document_export_request = cls(
            generation_id=generation_id,
            include_embeddings=include_embeddings,
        )

        return create_document_export_request
