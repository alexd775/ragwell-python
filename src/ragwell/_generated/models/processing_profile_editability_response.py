from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.processing_profile_editability_response_reason_code_type_0 import (
    ProcessingProfileEditabilityResponseReasonCodeType0,
)

T = TypeVar("T", bound="ProcessingProfileEditabilityResponse")


@_attrs_define
class ProcessingProfileEditabilityResponse:
    documents_present: bool
    editable: bool
    reason_code: None | ProcessingProfileEditabilityResponseReasonCodeType0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        documents_present = self.documents_present

        editable = self.editable

        reason_code: None | str
        if isinstance(
            self.reason_code, ProcessingProfileEditabilityResponseReasonCodeType0
        ):
            reason_code = self.reason_code.value
        else:
            reason_code = self.reason_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "documents_present": documents_present,
                "editable": editable,
                "reason_code": reason_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        documents_present = d.pop("documents_present")

        editable = d.pop("editable")

        def _parse_reason_code(
            data: object,
        ) -> None | ProcessingProfileEditabilityResponseReasonCodeType0:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reason_code_type_0 = (
                    ProcessingProfileEditabilityResponseReasonCodeType0(data)
                )

                return reason_code_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None | ProcessingProfileEditabilityResponseReasonCodeType0, data
            )

        reason_code = _parse_reason_code(d.pop("reason_code"))

        processing_profile_editability_response = cls(
            documents_present=documents_present,
            editable=editable,
            reason_code=reason_code,
        )

        processing_profile_editability_response.additional_properties = d
        return processing_profile_editability_response

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
