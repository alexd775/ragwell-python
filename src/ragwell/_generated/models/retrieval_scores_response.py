from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RetrievalScoresResponse")


@_attrs_define
class RetrievalScoresResponse:
    final: float
    text: float | None
    vector: float | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        final = self.final

        text: float | None
        text = self.text

        vector: float | None
        vector = self.vector

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "final": final,
                "text": text,
                "vector": vector,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        final = d.pop("final")

        def _parse_text(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        text = _parse_text(d.pop("text"))

        def _parse_vector(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        vector = _parse_vector(d.pop("vector"))

        retrieval_scores_response = cls(
            final=final,
            text=text,
            vector=vector,
        )

        retrieval_scores_response.additional_properties = d
        return retrieval_scores_response

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
