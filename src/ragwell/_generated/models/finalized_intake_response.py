from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.document_response import DocumentResponse
    from ..models.document_version_response import DocumentVersionResponse
    from ..models.upload_session_response import UploadSessionResponse


T = TypeVar("T", bound="FinalizedIntakeResponse")


@_attrs_define
class FinalizedIntakeResponse:
    document: DocumentResponse
    job_id: UUID
    upload: UploadSessionResponse
    version: DocumentVersionResponse
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        document = self.document.to_dict()

        job_id = str(self.job_id)

        upload = self.upload.to_dict()

        version = self.version.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "document": document,
                "job_id": job_id,
                "upload": upload,
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_response import DocumentResponse
        from ..models.document_version_response import DocumentVersionResponse
        from ..models.upload_session_response import UploadSessionResponse

        d = dict(src_dict)
        document = DocumentResponse.from_dict(d.pop("document"))

        job_id = UUID(d.pop("job_id"))

        upload = UploadSessionResponse.from_dict(d.pop("upload"))

        version = DocumentVersionResponse.from_dict(d.pop("version"))

        finalized_intake_response = cls(
            document=document,
            job_id=job_id,
            upload=upload,
            version=version,
        )

        finalized_intake_response.additional_properties = d
        return finalized_intake_response

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
