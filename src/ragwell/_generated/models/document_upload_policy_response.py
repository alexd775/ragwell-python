from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.accepted_document_format_response import (
        AcceptedDocumentFormatResponse,
    )
    from ..models.document_annotation_policy_response import (
        DocumentAnnotationPolicyResponse,
    )


T = TypeVar("T", bound="DocumentUploadPolicyResponse")


@_attrs_define
class DocumentUploadPolicyResponse:
    annotations: DocumentAnnotationPolicyResponse
    formats: list[AcceptedDocumentFormatResponse]
    text_page_equivalent_characters: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        annotations = self.annotations.to_dict()

        formats = []
        for formats_item_data in self.formats:
            formats_item = formats_item_data.to_dict()
            formats.append(formats_item)

        text_page_equivalent_characters = self.text_page_equivalent_characters

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotations": annotations,
                "formats": formats,
                "text_page_equivalent_characters": text_page_equivalent_characters,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.accepted_document_format_response import (
            AcceptedDocumentFormatResponse,
        )
        from ..models.document_annotation_policy_response import (
            DocumentAnnotationPolicyResponse,
        )

        d = dict(src_dict)
        annotations = DocumentAnnotationPolicyResponse.from_dict(d.pop("annotations"))

        formats = []
        _formats = d.pop("formats")
        for formats_item_data in _formats:
            formats_item = AcceptedDocumentFormatResponse.from_dict(formats_item_data)

            formats.append(formats_item)

        text_page_equivalent_characters = d.pop("text_page_equivalent_characters")

        document_upload_policy_response = cls(
            annotations=annotations,
            formats=formats,
            text_page_equivalent_characters=text_page_equivalent_characters,
        )

        document_upload_policy_response.additional_properties = d
        return document_upload_policy_response

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
