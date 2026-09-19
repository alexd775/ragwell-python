from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.limit_key import LimitKey
from ..models.limit_unit import LimitUnit
from ..models.plan_limit_error_detail_code import PlanLimitErrorDetailCode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.field_error import FieldError


T = TypeVar("T", bound="PlanLimitErrorDetail")


@_attrs_define
class PlanLimitErrorDetail:
    limit: int
    limit_key: LimitKey
    message: str
    remaining: int
    requested: int
    reserved: int
    reset_at: datetime.datetime | None
    unit: LimitUnit
    used: int
    code: PlanLimitErrorDetailCode | Unset = (
        PlanLimitErrorDetailCode.PLAN_LIMIT_EXCEEDED
    )
    field_errors: list[FieldError] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        limit = self.limit

        limit_key = self.limit_key.value

        message = self.message

        remaining = self.remaining

        requested = self.requested

        reserved = self.reserved

        reset_at: None | str
        if isinstance(self.reset_at, datetime.datetime):
            reset_at = self.reset_at.isoformat()
        else:
            reset_at = self.reset_at

        unit = self.unit.value

        used = self.used

        code: str | Unset = UNSET
        if not isinstance(self.code, Unset):
            code = self.code.value

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
                "limit": limit,
                "limit_key": limit_key,
                "message": message,
                "remaining": remaining,
                "requested": requested,
                "reserved": reserved,
                "reset_at": reset_at,
                "unit": unit,
                "used": used,
            }
        )
        if code is not UNSET:
            field_dict["code"] = code
        if field_errors is not UNSET:
            field_dict["field_errors"] = field_errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.field_error import FieldError

        d = dict(src_dict)
        limit = d.pop("limit")

        limit_key = LimitKey(d.pop("limit_key"))

        message = d.pop("message")

        remaining = d.pop("remaining")

        requested = d.pop("requested")

        reserved = d.pop("reserved")

        def _parse_reset_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reset_at_type_0 = datetime.datetime.fromisoformat(data)

                return reset_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        reset_at = _parse_reset_at(d.pop("reset_at"))

        unit = LimitUnit(d.pop("unit"))

        used = d.pop("used")

        _code = d.pop("code", UNSET)
        code: PlanLimitErrorDetailCode | Unset
        if isinstance(_code, Unset):
            code = UNSET
        else:
            code = PlanLimitErrorDetailCode(_code)

        _field_errors = d.pop("field_errors", UNSET)
        field_errors: list[FieldError] | Unset = UNSET
        if _field_errors is not UNSET:
            field_errors = []
            for field_errors_item_data in _field_errors:
                field_errors_item = FieldError.from_dict(field_errors_item_data)

                field_errors.append(field_errors_item)

        plan_limit_error_detail = cls(
            limit=limit,
            limit_key=limit_key,
            message=message,
            remaining=remaining,
            requested=requested,
            reserved=reserved,
            reset_at=reset_at,
            unit=unit,
            used=used,
            code=code,
            field_errors=field_errors,
        )

        plan_limit_error_detail.additional_properties = d
        return plan_limit_error_detail

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
