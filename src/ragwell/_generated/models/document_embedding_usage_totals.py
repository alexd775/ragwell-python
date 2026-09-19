from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DocumentEmbeddingUsageTotals")


@_attrs_define
class DocumentEmbeddingUsageTotals:
    accounted_input_tokens: int | None
    attempts_with_reported_usage: int
    customer_funded_attempt_count: int
    estimated_input_tokens: int
    operation_count: int
    plan_charged_input_tokens: int
    provider_reported_input_tokens: int | None
    submitted_attempt_count: int
    system_funded_attempt_count: int
    scope: Literal["selected_generation_all_attempts"] | Unset = (
        "selected_generation_all_attempts"
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        accounted_input_tokens: int | None
        accounted_input_tokens = self.accounted_input_tokens

        attempts_with_reported_usage = self.attempts_with_reported_usage

        customer_funded_attempt_count = self.customer_funded_attempt_count

        estimated_input_tokens = self.estimated_input_tokens

        operation_count = self.operation_count

        plan_charged_input_tokens = self.plan_charged_input_tokens

        provider_reported_input_tokens: int | None
        provider_reported_input_tokens = self.provider_reported_input_tokens

        submitted_attempt_count = self.submitted_attempt_count

        system_funded_attempt_count = self.system_funded_attempt_count

        scope = self.scope

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accounted_input_tokens": accounted_input_tokens,
                "attempts_with_reported_usage": attempts_with_reported_usage,
                "customer_funded_attempt_count": customer_funded_attempt_count,
                "estimated_input_tokens": estimated_input_tokens,
                "operation_count": operation_count,
                "plan_charged_input_tokens": plan_charged_input_tokens,
                "provider_reported_input_tokens": provider_reported_input_tokens,
                "submitted_attempt_count": submitted_attempt_count,
                "system_funded_attempt_count": system_funded_attempt_count,
            }
        )
        if scope is not UNSET:
            field_dict["scope"] = scope

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_accounted_input_tokens(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        accounted_input_tokens = _parse_accounted_input_tokens(
            d.pop("accounted_input_tokens")
        )

        attempts_with_reported_usage = d.pop("attempts_with_reported_usage")

        customer_funded_attempt_count = d.pop("customer_funded_attempt_count")

        estimated_input_tokens = d.pop("estimated_input_tokens")

        operation_count = d.pop("operation_count")

        plan_charged_input_tokens = d.pop("plan_charged_input_tokens")

        def _parse_provider_reported_input_tokens(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        provider_reported_input_tokens = _parse_provider_reported_input_tokens(
            d.pop("provider_reported_input_tokens")
        )

        submitted_attempt_count = d.pop("submitted_attempt_count")

        system_funded_attempt_count = d.pop("system_funded_attempt_count")

        scope = cast(
            Literal["selected_generation_all_attempts"] | Unset, d.pop("scope", UNSET)
        )
        if scope != "selected_generation_all_attempts" and not isinstance(scope, Unset):
            raise ValueError(
                f"scope must match const 'selected_generation_all_attempts', got '{scope}'"
            )

        document_embedding_usage_totals = cls(
            accounted_input_tokens=accounted_input_tokens,
            attempts_with_reported_usage=attempts_with_reported_usage,
            customer_funded_attempt_count=customer_funded_attempt_count,
            estimated_input_tokens=estimated_input_tokens,
            operation_count=operation_count,
            plan_charged_input_tokens=plan_charged_input_tokens,
            provider_reported_input_tokens=provider_reported_input_tokens,
            submitted_attempt_count=submitted_attempt_count,
            system_funded_attempt_count=system_funded_attempt_count,
            scope=scope,
        )

        document_embedding_usage_totals.additional_properties = d
        return document_embedding_usage_totals

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
