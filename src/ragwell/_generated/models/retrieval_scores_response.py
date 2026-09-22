from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RetrievalScoresResponse")


@_attrs_define
class RetrievalScoresResponse:
    final: float
    text: float | None
    vector: float | None
    hybrid: float | None | Unset = UNSET
    rerank: float | None | Unset = UNSET
    rerank_confidence: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        final = self.final

        text: float | None
        text = self.text

        vector: float | None
        vector = self.vector

        hybrid: float | None | Unset
        if isinstance(self.hybrid, Unset):
            hybrid = UNSET
        else:
            hybrid = self.hybrid

        rerank: float | None | Unset
        if isinstance(self.rerank, Unset):
            rerank = UNSET
        else:
            rerank = self.rerank

        rerank_confidence: float | None | Unset
        if isinstance(self.rerank_confidence, Unset):
            rerank_confidence = UNSET
        else:
            rerank_confidence = self.rerank_confidence

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "final": final,
                "text": text,
                "vector": vector,
            }
        )
        if hybrid is not UNSET:
            field_dict["hybrid"] = hybrid
        if rerank is not UNSET:
            field_dict["rerank"] = rerank
        if rerank_confidence is not UNSET:
            field_dict["rerank_confidence"] = rerank_confidence

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

        def _parse_hybrid(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        hybrid = _parse_hybrid(d.pop("hybrid", UNSET))

        def _parse_rerank(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rerank = _parse_rerank(d.pop("rerank", UNSET))

        def _parse_rerank_confidence(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rerank_confidence = _parse_rerank_confidence(d.pop("rerank_confidence", UNSET))

        retrieval_scores_response = cls(
            final=final,
            text=text,
            vector=vector,
            hybrid=hybrid,
            rerank=rerank,
            rerank_confidence=rerank_confidence,
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
