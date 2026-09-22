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

from ..models.rerank_metadata_provider import RerankMetadataProvider
from ..types import UNSET, Unset

T = TypeVar("T", bound="RerankMetadata")


@_attrs_define
class RerankMetadata:
    applied: bool
    candidate_count: int
    configuration_revision: int
    model: str
    id: Literal["jev"] | Unset = "jev"
    policy: str | Unset = "jev-relevance-v1"
    provider: RerankMetadataProvider | Unset = RerankMetadataProvider.TYPESAFE
    resolved_model: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        applied = self.applied

        candidate_count = self.candidate_count

        configuration_revision = self.configuration_revision

        model = self.model

        id = self.id

        policy = self.policy

        provider: str | Unset = UNSET
        if not isinstance(self.provider, Unset):
            provider = self.provider.value

        resolved_model: None | str | Unset
        if isinstance(self.resolved_model, Unset):
            resolved_model = UNSET
        else:
            resolved_model = self.resolved_model

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "applied": applied,
                "candidate_count": candidate_count,
                "configuration_revision": configuration_revision,
                "model": model,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if policy is not UNSET:
            field_dict["policy"] = policy
        if provider is not UNSET:
            field_dict["provider"] = provider
        if resolved_model is not UNSET:
            field_dict["resolved_model"] = resolved_model

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        applied = d.pop("applied")

        candidate_count = d.pop("candidate_count")

        configuration_revision = d.pop("configuration_revision")

        model = d.pop("model")

        id = cast(Literal["jev"] | Unset, d.pop("id", UNSET))
        if id != "jev" and not isinstance(id, Unset):
            raise ValueError(f"id must match const 'jev', got '{id}'")

        policy = d.pop("policy", UNSET)

        _provider = d.pop("provider", UNSET)
        provider: RerankMetadataProvider | Unset
        if isinstance(_provider, Unset):
            provider = UNSET
        else:
            provider = RerankMetadataProvider(_provider)

        def _parse_resolved_model(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        resolved_model = _parse_resolved_model(d.pop("resolved_model", UNSET))

        rerank_metadata = cls(
            applied=applied,
            candidate_count=candidate_count,
            configuration_revision=configuration_revision,
            model=model,
            id=id,
            policy=policy,
            provider=provider,
            resolved_model=resolved_model,
        )

        rerank_metadata.additional_properties = d
        return rerank_metadata

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
