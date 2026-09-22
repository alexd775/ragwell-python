from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rerank_request import RerankRequest
    from ..models.search_filters import SearchFilters


T = TypeVar("T", bound="SearchRequest")


@_attrs_define
class SearchRequest:
    query: str
    filters: None | SearchFilters | Unset = UNSET
    k: int | Unset = 5
    rerank: None | RerankRequest | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.rerank_request import RerankRequest
        from ..models.search_filters import SearchFilters

        query = self.query

        filters: dict[str, Any] | None | Unset
        if isinstance(self.filters, Unset):
            filters = UNSET
        elif isinstance(self.filters, SearchFilters):
            filters = self.filters.to_dict()
        else:
            filters = self.filters

        k = self.k

        rerank: dict[str, Any] | None | Unset
        if isinstance(self.rerank, Unset):
            rerank = UNSET
        elif isinstance(self.rerank, RerankRequest):
            rerank = self.rerank.to_dict()
        else:
            rerank = self.rerank

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "query": query,
            }
        )
        if filters is not UNSET:
            field_dict["filters"] = filters
        if k is not UNSET:
            field_dict["k"] = k
        if rerank is not UNSET:
            field_dict["rerank"] = rerank

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rerank_request import RerankRequest
        from ..models.search_filters import SearchFilters

        d = dict(src_dict)
        query = d.pop("query")

        def _parse_filters(data: object) -> None | SearchFilters | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                filters_type_0 = SearchFilters.from_dict(data)

                return filters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SearchFilters | Unset, data)

        filters = _parse_filters(d.pop("filters", UNSET))

        k = d.pop("k", UNSET)

        def _parse_rerank(data: object) -> None | RerankRequest | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rerank_type_0 = RerankRequest.from_dict(data)

                return rerank_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RerankRequest | Unset, data)

        rerank = _parse_rerank(d.pop("rerank", UNSET))

        search_request = cls(
            query=query,
            filters=filters,
            k=k,
            rerank=rerank,
        )

        return search_request
