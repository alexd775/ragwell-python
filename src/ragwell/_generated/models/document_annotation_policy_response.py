from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.document_annotation_field_response import (
        DocumentAnnotationFieldResponse,
    )


T = TypeVar("T", bound="DocumentAnnotationPolicyResponse")


@_attrs_define
class DocumentAnnotationPolicyResponse:
    fields: list[DocumentAnnotationFieldResponse]
    maximum_document_ids: int
    maximum_filter_terms: int
    maximum_tags: int
    maximum_total_bytes: int
    tag_maximum_bytes: int
    tag_maximum_characters: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fields = []
        for fields_item_data in self.fields:
            fields_item = fields_item_data.to_dict()
            fields.append(fields_item)

        maximum_document_ids = self.maximum_document_ids

        maximum_filter_terms = self.maximum_filter_terms

        maximum_tags = self.maximum_tags

        maximum_total_bytes = self.maximum_total_bytes

        tag_maximum_bytes = self.tag_maximum_bytes

        tag_maximum_characters = self.tag_maximum_characters

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fields": fields,
                "maximum_document_ids": maximum_document_ids,
                "maximum_filter_terms": maximum_filter_terms,
                "maximum_tags": maximum_tags,
                "maximum_total_bytes": maximum_total_bytes,
                "tag_maximum_bytes": tag_maximum_bytes,
                "tag_maximum_characters": tag_maximum_characters,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_annotation_field_response import (
            DocumentAnnotationFieldResponse,
        )

        d = dict(src_dict)
        fields = []
        _fields = d.pop("fields")
        for fields_item_data in _fields:
            fields_item = DocumentAnnotationFieldResponse.from_dict(fields_item_data)

            fields.append(fields_item)

        maximum_document_ids = d.pop("maximum_document_ids")

        maximum_filter_terms = d.pop("maximum_filter_terms")

        maximum_tags = d.pop("maximum_tags")

        maximum_total_bytes = d.pop("maximum_total_bytes")

        tag_maximum_bytes = d.pop("tag_maximum_bytes")

        tag_maximum_characters = d.pop("tag_maximum_characters")

        document_annotation_policy_response = cls(
            fields=fields,
            maximum_document_ids=maximum_document_ids,
            maximum_filter_terms=maximum_filter_terms,
            maximum_tags=maximum_tags,
            maximum_total_bytes=maximum_total_bytes,
            tag_maximum_bytes=tag_maximum_bytes,
            tag_maximum_characters=tag_maximum_characters,
        )

        document_annotation_policy_response.additional_properties = d
        return document_annotation_policy_response

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
