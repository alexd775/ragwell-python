from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.document_storage_editability_response_reason_code_type_0 import (
    DocumentStorageEditabilityResponseReasonCodeType0,
)

T = TypeVar("T", bound="DocumentStorageEditabilityResponse")


@_attrs_define
class DocumentStorageEditabilityResponse:
    editable: bool
    reason_code: DocumentStorageEditabilityResponseReasonCodeType0 | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        editable = self.editable

        reason_code: None | str
        if isinstance(
            self.reason_code, DocumentStorageEditabilityResponseReasonCodeType0
        ):
            reason_code = self.reason_code.value
        else:
            reason_code = self.reason_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "editable": editable,
                "reason_code": reason_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        editable = d.pop("editable")

        def _parse_reason_code(
            data: object,
        ) -> DocumentStorageEditabilityResponseReasonCodeType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reason_code_type_0 = DocumentStorageEditabilityResponseReasonCodeType0(
                    data
                )

                return reason_code_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DocumentStorageEditabilityResponseReasonCodeType0 | None, data)

        reason_code = _parse_reason_code(d.pop("reason_code"))

        document_storage_editability_response = cls(
            editable=editable,
            reason_code=reason_code,
        )

        document_storage_editability_response.additional_properties = d
        return document_storage_editability_response

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
