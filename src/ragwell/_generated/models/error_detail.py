from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.field_error import FieldError


T = TypeVar("T", bound="ErrorDetail")


@_attrs_define
class ErrorDetail:
    code: str
    message: str
    field_errors: list[FieldError] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        message = self.message

        field_errors: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.field_errors, Unset):
            field_errors = []
            for field_errors_item_data in self.field_errors:
                field_errors_item = field_errors_item_data.to_dict()
                field_errors.append(field_errors_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
                "message": message,
            }
        )
        if field_errors is not UNSET:
            field_dict["field_errors"] = field_errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.field_error import FieldError

        d = dict(src_dict)
        code = d.pop("code")

        message = d.pop("message")

        _field_errors = d.pop("field_errors", UNSET)
        field_errors: list[FieldError] | Unset = UNSET
        if _field_errors is not UNSET:
            field_errors = []
            for field_errors_item_data in _field_errors:
                field_errors_item = FieldError.from_dict(field_errors_item_data)

                field_errors.append(field_errors_item)

        error_detail = cls(
            code=code,
            message=message,
            field_errors=field_errors,
        )

        error_detail.additional_properties = d
        return error_detail

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
