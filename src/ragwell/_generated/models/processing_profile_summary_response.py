from __future__ import annotations

from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.processing_profile_technical_response import (
        ProcessingProfileTechnicalResponse,
    )


T = TypeVar("T", bound="ProcessingProfileSummaryResponse")


@_attrs_define
class ProcessingProfileSummaryResponse:
    chunking_option_id: str
    chunking_summary: str
    description: str
    display_name: str
    embedding_option_id: str
    embedding_summary: str
    extraction_summary: str
    id: str
    management: Literal["ragbox_managed"]
    retrieval_summary: str
    technical: ProcessingProfileTechnicalResponse
    version: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chunking_option_id = self.chunking_option_id

        chunking_summary = self.chunking_summary

        description = self.description

        display_name = self.display_name

        embedding_option_id = self.embedding_option_id

        embedding_summary = self.embedding_summary

        extraction_summary = self.extraction_summary

        id = self.id

        management = self.management

        retrieval_summary = self.retrieval_summary

        technical = self.technical.to_dict()

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "chunking_option_id": chunking_option_id,
                "chunking_summary": chunking_summary,
                "description": description,
                "display_name": display_name,
                "embedding_option_id": embedding_option_id,
                "embedding_summary": embedding_summary,
                "extraction_summary": extraction_summary,
                "id": id,
                "management": management,
                "retrieval_summary": retrieval_summary,
                "technical": technical,
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.processing_profile_technical_response import (
            ProcessingProfileTechnicalResponse,
        )

        d = dict(src_dict)
        chunking_option_id = d.pop("chunking_option_id")

        chunking_summary = d.pop("chunking_summary")

        description = d.pop("description")

        display_name = d.pop("display_name")

        embedding_option_id = d.pop("embedding_option_id")

        embedding_summary = d.pop("embedding_summary")

        extraction_summary = d.pop("extraction_summary")

        id = d.pop("id")

        management = cast(Literal["ragbox_managed"], d.pop("management"))
        if management != "ragbox_managed":
            raise ValueError(
                f"management must match const 'ragbox_managed', got '{management}'"
            )

        retrieval_summary = d.pop("retrieval_summary")

        technical = ProcessingProfileTechnicalResponse.from_dict(d.pop("technical"))

        version = d.pop("version")

        processing_profile_summary_response = cls(
            chunking_option_id=chunking_option_id,
            chunking_summary=chunking_summary,
            description=description,
            display_name=display_name,
            embedding_option_id=embedding_option_id,
            embedding_summary=embedding_summary,
            extraction_summary=extraction_summary,
            id=id,
            management=management,
            retrieval_summary=retrieval_summary,
            technical=technical,
            version=version,
        )

        processing_profile_summary_response.additional_properties = d
        return processing_profile_summary_response

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
