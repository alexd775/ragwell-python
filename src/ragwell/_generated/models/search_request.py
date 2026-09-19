from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_filters import SearchFilters


T = TypeVar("T", bound="SearchRequest")


@_attrs_define
class SearchRequest:
    query: str
    filters: None | SearchFilters | Unset = UNSET
    k: int | Unset = 5

    def to_dict(self) -> dict[str, Any]:
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
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

        search_request = cls(
            query=query,
            filters=filters,
            k=k,
        )

        return search_request
