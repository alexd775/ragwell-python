from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.create_upload_request_declared_media_type import (
    CreateUploadRequestDeclaredMediaType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_metadata_input import DocumentMetadataInput


T = TypeVar("T", bound="CreateUploadRequest")


@_attrs_define
class CreateUploadRequest:
    declared_media_type: CreateUploadRequestDeclaredMediaType
    declared_sha256: str
    declared_size_bytes: int
    original_filename: str
    metadata: DocumentMetadataInput | Unset = UNSET
    tags: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        declared_media_type = self.declared_media_type.value

        declared_sha256 = self.declared_sha256

        declared_size_bytes = self.declared_size_bytes

        original_filename = self.original_filename

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "declared_media_type": declared_media_type,
                "declared_sha256": declared_sha256,
                "declared_size_bytes": declared_size_bytes,
                "original_filename": original_filename,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_metadata_input import DocumentMetadataInput

        d = dict(src_dict)
        declared_media_type = CreateUploadRequestDeclaredMediaType(
            d.pop("declared_media_type")
        )

        declared_sha256 = d.pop("declared_sha256")

        declared_size_bytes = d.pop("declared_size_bytes")

        original_filename = d.pop("original_filename")

        _metadata = d.pop("metadata", UNSET)
        metadata: DocumentMetadataInput | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = DocumentMetadataInput.from_dict(_metadata)

        tags = cast(list[str], d.pop("tags", UNSET))

        create_upload_request = cls(
            declared_media_type=declared_media_type,
            declared_sha256=declared_sha256,
            declared_size_bytes=declared_size_bytes,
            original_filename=original_filename,
            metadata=metadata,
            tags=tags,
        )

        return create_upload_request
