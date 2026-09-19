from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.document_metadata_input import DocumentMetadataInput


T = TypeVar("T", bound="ReplaceDocumentMetadataRequest")


@_attrs_define
class ReplaceDocumentMetadataRequest:
    expected_revision: int
    metadata: DocumentMetadataInput
    tags: list[str]

    def to_dict(self) -> dict[str, Any]:
        expected_revision = self.expected_revision

        metadata = self.metadata.to_dict()

        tags = self.tags

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "expected_revision": expected_revision,
                "metadata": metadata,
                "tags": tags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_metadata_input import DocumentMetadataInput

        d = dict(src_dict)
        expected_revision = d.pop("expected_revision")

        metadata = DocumentMetadataInput.from_dict(d.pop("metadata"))

        tags = cast(list[str], d.pop("tags"))

        replace_document_metadata_request = cls(
            expected_revision=expected_revision,
            metadata=metadata,
            tags=tags,
        )

        return replace_document_metadata_request
