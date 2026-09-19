from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.processing_service_class_id import ProcessingServiceClassId

T = TypeVar("T", bound="ProcessingServiceClassResponse")


@_attrs_define
class ProcessingServiceClassResponse:
    display_name: str
    id: ProcessingServiceClassId
    queue_guidance: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        id = self.id.value

        queue_guidance = self.queue_guidance

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "display_name": display_name,
                "id": id,
                "queue_guidance": queue_guidance,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        display_name = d.pop("display_name")

        id = ProcessingServiceClassId(d.pop("id"))

        queue_guidance = d.pop("queue_guidance")

        processing_service_class_response = cls(
            display_name=display_name,
            id=id,
            queue_guidance=queue_guidance,
        )

        processing_service_class_response.additional_properties = d
        return processing_service_class_response

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
