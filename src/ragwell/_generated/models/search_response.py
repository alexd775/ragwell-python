from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rerank_metadata import RerankMetadata
    from ..models.retrieval_item_response import RetrievalItemResponse


T = TypeVar("T", bound="SearchResponse")


@_attrs_define
class SearchResponse:
    items: list[RetrievalItemResponse]
    profile_id: None | str
    retrieval_id: UUID
    retrieval_version: str
    rerank: None | RerankMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.rerank_metadata import RerankMetadata

        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        profile_id: None | str
        profile_id = self.profile_id

        retrieval_id = str(self.retrieval_id)

        retrieval_version = self.retrieval_version

        rerank: dict[str, Any] | None | Unset
        if isinstance(self.rerank, Unset):
            rerank = UNSET
        elif isinstance(self.rerank, RerankMetadata):
            rerank = self.rerank.to_dict()
        else:
            rerank = self.rerank

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "items": items,
                "profile_id": profile_id,
                "retrieval_id": retrieval_id,
                "retrieval_version": retrieval_version,
            }
        )
        if rerank is not UNSET:
            field_dict["rerank"] = rerank

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rerank_metadata import RerankMetadata
        from ..models.retrieval_item_response import RetrievalItemResponse

        d = dict(src_dict)
        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = RetrievalItemResponse.from_dict(items_item_data)

            items.append(items_item)

        def _parse_profile_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        profile_id = _parse_profile_id(d.pop("profile_id"))

        retrieval_id = UUID(d.pop("retrieval_id"))

        retrieval_version = d.pop("retrieval_version")

        def _parse_rerank(data: object) -> None | RerankMetadata | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rerank_type_0 = RerankMetadata.from_dict(data)

                return rerank_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RerankMetadata | Unset, data)

        rerank = _parse_rerank(d.pop("rerank", UNSET))

        search_response = cls(
            items=items,
            profile_id=profile_id,
            retrieval_id=retrieval_id,
            retrieval_version=retrieval_version,
            rerank=rerank,
        )

        search_response.additional_properties = d
        return search_response

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
