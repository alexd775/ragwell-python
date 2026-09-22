from __future__ import annotations

from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rerank_params import RerankParams


T = TypeVar("T", bound="RerankRequest")


@_attrs_define
class RerankRequest:
    id: Literal["jev"]
    params: RerankParams | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        params: dict[str, Any] | Unset = UNSET
        if not isinstance(self.params, Unset):
            params = self.params.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "id": id,
            }
        )
        if params is not UNSET:
            field_dict["params"] = params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rerank_params import RerankParams

        d = dict(src_dict)
        id = cast(Literal["jev"], d.pop("id"))
        if id != "jev":
            raise ValueError(f"id must match const 'jev', got '{id}'")

        _params = d.pop("params", UNSET)
        params: RerankParams | Unset
        if isinstance(_params, Unset):
            params = UNSET
        else:
            params = RerankParams.from_dict(_params)

        rerank_request = cls(
            id=id,
            params=params,
        )

        return rerank_request
