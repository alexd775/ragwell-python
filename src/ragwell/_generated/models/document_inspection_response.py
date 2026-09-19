from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.document_embedding_usage import DocumentEmbeddingUsage
    from ..models.document_generation_info import DocumentGenerationInfo
    from ..models.document_job_info import DocumentJobInfo
    from ..models.document_profile_info import DocumentProfileInfo
    from ..models.document_source_info import DocumentSourceInfo
    from ..models.document_stage_attempt import DocumentStageAttempt


T = TypeVar("T", bound="DocumentInspectionResponse")


@_attrs_define
class DocumentInspectionResponse:
    active_generation_id: None | UUID
    attempts: list[DocumentStageAttempt]
    attempts_truncated: bool
    deletion_receipt_id: None | UUID
    document_id: UUID
    embedding_usage: DocumentEmbeddingUsage | None
    job_details_permitted: bool
    latest_job: DocumentJobInfo | None
    measured_at: datetime.datetime
    profile: DocumentProfileInfo | None
    searchable: bool
    selected_generation: DocumentGenerationInfo | None
    selected_job: DocumentJobInfo | None
    source: DocumentSourceInfo | None
    warnings: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.document_embedding_usage import DocumentEmbeddingUsage
        from ..models.document_generation_info import DocumentGenerationInfo
        from ..models.document_job_info import DocumentJobInfo
        from ..models.document_profile_info import DocumentProfileInfo
        from ..models.document_source_info import DocumentSourceInfo

        active_generation_id: None | str
        if isinstance(self.active_generation_id, UUID):
            active_generation_id = str(self.active_generation_id)
        else:
            active_generation_id = self.active_generation_id

        attempts = []
        for attempts_item_data in self.attempts:
            attempts_item = attempts_item_data.to_dict()
            attempts.append(attempts_item)

        attempts_truncated = self.attempts_truncated

        deletion_receipt_id: None | str
        if isinstance(self.deletion_receipt_id, UUID):
            deletion_receipt_id = str(self.deletion_receipt_id)
        else:
            deletion_receipt_id = self.deletion_receipt_id

        document_id = str(self.document_id)

        embedding_usage: dict[str, Any] | None
        if isinstance(self.embedding_usage, DocumentEmbeddingUsage):
            embedding_usage = self.embedding_usage.to_dict()
        else:
            embedding_usage = self.embedding_usage

        job_details_permitted = self.job_details_permitted

        latest_job: dict[str, Any] | None
        if isinstance(self.latest_job, DocumentJobInfo):
            latest_job = self.latest_job.to_dict()
        else:
            latest_job = self.latest_job

        measured_at = self.measured_at.isoformat()

        profile: dict[str, Any] | None
        if isinstance(self.profile, DocumentProfileInfo):
            profile = self.profile.to_dict()
        else:
            profile = self.profile

        searchable = self.searchable

        selected_generation: dict[str, Any] | None
        if isinstance(self.selected_generation, DocumentGenerationInfo):
            selected_generation = self.selected_generation.to_dict()
        else:
            selected_generation = self.selected_generation

        selected_job: dict[str, Any] | None
        if isinstance(self.selected_job, DocumentJobInfo):
            selected_job = self.selected_job.to_dict()
        else:
            selected_job = self.selected_job

        source: dict[str, Any] | None
        if isinstance(self.source, DocumentSourceInfo):
            source = self.source.to_dict()
        else:
            source = self.source

        warnings = self.warnings

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "active_generation_id": active_generation_id,
                "attempts": attempts,
                "attempts_truncated": attempts_truncated,
                "deletion_receipt_id": deletion_receipt_id,
                "document_id": document_id,
                "embedding_usage": embedding_usage,
                "job_details_permitted": job_details_permitted,
                "latest_job": latest_job,
                "measured_at": measured_at,
                "profile": profile,
                "searchable": searchable,
                "selected_generation": selected_generation,
                "selected_job": selected_job,
                "source": source,
                "warnings": warnings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_embedding_usage import DocumentEmbeddingUsage
        from ..models.document_generation_info import DocumentGenerationInfo
        from ..models.document_job_info import DocumentJobInfo
        from ..models.document_profile_info import DocumentProfileInfo
        from ..models.document_source_info import DocumentSourceInfo
        from ..models.document_stage_attempt import DocumentStageAttempt

        d = dict(src_dict)

        def _parse_active_generation_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                active_generation_id_type_0 = UUID(data)

                return active_generation_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        active_generation_id = _parse_active_generation_id(
            d.pop("active_generation_id")
        )

        attempts = []
        _attempts = d.pop("attempts")
        for attempts_item_data in _attempts:
            attempts_item = DocumentStageAttempt.from_dict(attempts_item_data)

            attempts.append(attempts_item)

        attempts_truncated = d.pop("attempts_truncated")

        def _parse_deletion_receipt_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deletion_receipt_id_type_0 = UUID(data)

                return deletion_receipt_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        deletion_receipt_id = _parse_deletion_receipt_id(d.pop("deletion_receipt_id"))

        document_id = UUID(d.pop("document_id"))

        def _parse_embedding_usage(data: object) -> DocumentEmbeddingUsage | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                embedding_usage_type_0 = DocumentEmbeddingUsage.from_dict(data)

                return embedding_usage_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentEmbeddingUsage | None, data)

        embedding_usage = _parse_embedding_usage(d.pop("embedding_usage"))

        job_details_permitted = d.pop("job_details_permitted")

        def _parse_latest_job(data: object) -> DocumentJobInfo | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                latest_job_type_0 = DocumentJobInfo.from_dict(data)

                return latest_job_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentJobInfo | None, data)

        latest_job = _parse_latest_job(d.pop("latest_job"))

        measured_at = datetime.datetime.fromisoformat(d.pop("measured_at"))

        def _parse_profile(data: object) -> DocumentProfileInfo | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                profile_type_0 = DocumentProfileInfo.from_dict(data)

                return profile_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentProfileInfo | None, data)

        profile = _parse_profile(d.pop("profile"))

        searchable = d.pop("searchable")

        def _parse_selected_generation(data: object) -> DocumentGenerationInfo | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                selected_generation_type_0 = DocumentGenerationInfo.from_dict(data)

                return selected_generation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentGenerationInfo | None, data)

        selected_generation = _parse_selected_generation(d.pop("selected_generation"))

        def _parse_selected_job(data: object) -> DocumentJobInfo | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                selected_job_type_0 = DocumentJobInfo.from_dict(data)

                return selected_job_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentJobInfo | None, data)

        selected_job = _parse_selected_job(d.pop("selected_job"))

        def _parse_source(data: object) -> DocumentSourceInfo | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_type_0 = DocumentSourceInfo.from_dict(data)

                return source_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentSourceInfo | None, data)

        source = _parse_source(d.pop("source"))

        warnings = cast(list[str], d.pop("warnings"))

        document_inspection_response = cls(
            active_generation_id=active_generation_id,
            attempts=attempts,
            attempts_truncated=attempts_truncated,
            deletion_receipt_id=deletion_receipt_id,
            document_id=document_id,
            embedding_usage=embedding_usage,
            job_details_permitted=job_details_permitted,
            latest_job=latest_job,
            measured_at=measured_at,
            profile=profile,
            searchable=searchable,
            selected_generation=selected_generation,
            selected_job=selected_job,
            source=source,
            warnings=warnings,
        )

        document_inspection_response.additional_properties = d
        return document_inspection_response

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
