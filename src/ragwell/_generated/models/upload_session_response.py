from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.upload_state import UploadState

if TYPE_CHECKING:
    from ..models.document_metadata_response import DocumentMetadataResponse


T = TypeVar("T", bound="UploadSessionResponse")


@_attrs_define
class UploadSessionResponse:
    created_at: datetime.datetime
    declared_media_type: str
    declared_sha256: str
    declared_size_bytes: int
    document_id: None | UUID
    document_version_id: None | UUID
    expires_at: datetime.datetime
    finalized_at: datetime.datetime | None
    id: UUID
    job_id: None | UUID
    metadata: DocumentMetadataResponse
    original_filename: str
    rejection_code: None | str
    state: UploadState
    tags: list[str]
    uploaded_at: datetime.datetime | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        declared_media_type = self.declared_media_type

        declared_sha256 = self.declared_sha256

        declared_size_bytes = self.declared_size_bytes

        document_id: None | str
        if isinstance(self.document_id, UUID):
            document_id = str(self.document_id)
        else:
            document_id = self.document_id

        document_version_id: None | str
        if isinstance(self.document_version_id, UUID):
            document_version_id = str(self.document_version_id)
        else:
            document_version_id = self.document_version_id

        expires_at = self.expires_at.isoformat()

        finalized_at: None | str
        if isinstance(self.finalized_at, datetime.datetime):
            finalized_at = self.finalized_at.isoformat()
        else:
            finalized_at = self.finalized_at

        id = str(self.id)

        job_id: None | str
        if isinstance(self.job_id, UUID):
            job_id = str(self.job_id)
        else:
            job_id = self.job_id

        metadata = self.metadata.to_dict()

        original_filename = self.original_filename

        rejection_code: None | str
        rejection_code = self.rejection_code

        state = self.state.value

        tags = self.tags

        uploaded_at: None | str
        if isinstance(self.uploaded_at, datetime.datetime):
            uploaded_at = self.uploaded_at.isoformat()
        else:
            uploaded_at = self.uploaded_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "declared_media_type": declared_media_type,
                "declared_sha256": declared_sha256,
                "declared_size_bytes": declared_size_bytes,
                "document_id": document_id,
                "document_version_id": document_version_id,
                "expires_at": expires_at,
                "finalized_at": finalized_at,
                "id": id,
                "job_id": job_id,
                "metadata": metadata,
                "original_filename": original_filename,
                "rejection_code": rejection_code,
                "state": state,
                "tags": tags,
                "uploaded_at": uploaded_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_metadata_response import DocumentMetadataResponse

        d = dict(src_dict)
        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        declared_media_type = d.pop("declared_media_type")

        declared_sha256 = d.pop("declared_sha256")

        declared_size_bytes = d.pop("declared_size_bytes")

        def _parse_document_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                document_id_type_0 = UUID(data)

                return document_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        document_id = _parse_document_id(d.pop("document_id"))

        def _parse_document_version_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                document_version_id_type_0 = UUID(data)

                return document_version_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        document_version_id = _parse_document_version_id(d.pop("document_version_id"))

        expires_at = datetime.datetime.fromisoformat(d.pop("expires_at"))

        def _parse_finalized_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                finalized_at_type_0 = datetime.datetime.fromisoformat(data)

                return finalized_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        finalized_at = _parse_finalized_at(d.pop("finalized_at"))

        id = UUID(d.pop("id"))

        def _parse_job_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                job_id_type_0 = UUID(data)

                return job_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        job_id = _parse_job_id(d.pop("job_id"))

        metadata = DocumentMetadataResponse.from_dict(d.pop("metadata"))

        original_filename = d.pop("original_filename")

        def _parse_rejection_code(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        rejection_code = _parse_rejection_code(d.pop("rejection_code"))

        state = UploadState(d.pop("state"))

        tags = cast(list[str], d.pop("tags"))

        def _parse_uploaded_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                uploaded_at_type_0 = datetime.datetime.fromisoformat(data)

                return uploaded_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        uploaded_at = _parse_uploaded_at(d.pop("uploaded_at"))

        upload_session_response = cls(
            created_at=created_at,
            declared_media_type=declared_media_type,
            declared_sha256=declared_sha256,
            declared_size_bytes=declared_size_bytes,
            document_id=document_id,
            document_version_id=document_version_id,
            expires_at=expires_at,
            finalized_at=finalized_at,
            id=id,
            job_id=job_id,
            metadata=metadata,
            original_filename=original_filename,
            rejection_code=rejection_code,
            state=state,
            tags=tags,
            uploaded_at=uploaded_at,
        )

        upload_session_response.additional_properties = d
        return upload_session_response

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
