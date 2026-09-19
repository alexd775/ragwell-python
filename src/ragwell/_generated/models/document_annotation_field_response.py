from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.document_annotation_field_response_key import (
    DocumentAnnotationFieldResponseKey,
)

T = TypeVar("T", bound="DocumentAnnotationFieldResponse")


@_attrs_define
class DocumentAnnotationFieldResponse:
    display_name: str
    key: DocumentAnnotationFieldResponseKey
    maximum_bytes: int
    maximum_characters: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        key = self.key.value

        maximum_bytes = self.maximum_bytes

        maximum_characters = self.maximum_characters

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "display_name": display_name,
                "key": key,
                "maximum_bytes": maximum_bytes,
                "maximum_characters": maximum_characters,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        display_name = d.pop("display_name")

        key = DocumentAnnotationFieldResponseKey(d.pop("key"))

        maximum_bytes = d.pop("maximum_bytes")

        maximum_characters = d.pop("maximum_characters")

        document_annotation_field_response = cls(
            display_name=display_name,
            key=key,
            maximum_bytes=maximum_bytes,
            maximum_characters=maximum_characters,
        )

        document_annotation_field_response.additional_properties = d
        return document_annotation_field_response

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
