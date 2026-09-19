from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.processing_profile_editability_response import (
        ProcessingProfileEditabilityResponse,
    )
    from ..models.processing_profile_summary_response import (
        ProcessingProfileSummaryResponse,
    )


T = TypeVar("T", bound="ProjectResponse")


@_attrs_define
class ProjectResponse:
    active_processing_profile: ProcessingProfileSummaryResponse
    created_at: datetime.datetime
    description: None | str
    id: UUID
    name: str
    processing_profile_editability: ProcessingProfileEditabilityResponse
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        active_processing_profile = self.active_processing_profile.to_dict()

        created_at = self.created_at.isoformat()

        description: None | str
        description = self.description

        id = str(self.id)

        name = self.name

        processing_profile_editability = self.processing_profile_editability.to_dict()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "active_processing_profile": active_processing_profile,
                "created_at": created_at,
                "description": description,
                "id": id,
                "name": name,
                "processing_profile_editability": processing_profile_editability,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.processing_profile_editability_response import (
            ProcessingProfileEditabilityResponse,
        )
        from ..models.processing_profile_summary_response import (
            ProcessingProfileSummaryResponse,
        )

        d = dict(src_dict)
        active_processing_profile = ProcessingProfileSummaryResponse.from_dict(
            d.pop("active_processing_profile")
        )

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        id = UUID(d.pop("id"))

        name = d.pop("name")

        processing_profile_editability = ProcessingProfileEditabilityResponse.from_dict(
            d.pop("processing_profile_editability")
        )

        updated_at = datetime.datetime.fromisoformat(d.pop("updated_at"))

        project_response = cls(
            active_processing_profile=active_processing_profile,
            created_at=created_at,
            description=description,
            id=id,
            name=name,
            processing_profile_editability=processing_profile_editability,
            updated_at=updated_at,
        )

        project_response.additional_properties = d
        return project_response

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
