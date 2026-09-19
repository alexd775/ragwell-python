from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.embedding_connection_notice_response_lane import (
    EmbeddingConnectionNoticeResponseLane,
)
from ..models.embedding_connection_notice_response_state import (
    EmbeddingConnectionNoticeResponseState,
)

T = TypeVar("T", bound="EmbeddingConnectionNoticeResponse")


@_attrs_define
class EmbeddingConnectionNoticeResponse:
    code: str
    id: UUID
    intervention_required: bool
    lane: EmbeddingConnectionNoticeResponseLane
    opened_at: datetime.datetime
    recovered_at: datetime.datetime | None
    state: EmbeddingConnectionNoticeResponseState
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        id = str(self.id)

        intervention_required = self.intervention_required

        lane = self.lane.value

        opened_at = self.opened_at.isoformat()

        recovered_at: None | str
        if isinstance(self.recovered_at, datetime.datetime):
            recovered_at = self.recovered_at.isoformat()
        else:
            recovered_at = self.recovered_at

        state = self.state.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
                "id": id,
                "intervention_required": intervention_required,
                "lane": lane,
                "opened_at": opened_at,
                "recovered_at": recovered_at,
                "state": state,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = d.pop("code")

        id = UUID(d.pop("id"))

        intervention_required = d.pop("intervention_required")

        lane = EmbeddingConnectionNoticeResponseLane(d.pop("lane"))

        opened_at = datetime.datetime.fromisoformat(d.pop("opened_at"))

        def _parse_recovered_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                recovered_at_type_0 = datetime.datetime.fromisoformat(data)

                return recovered_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        recovered_at = _parse_recovered_at(d.pop("recovered_at"))

        state = EmbeddingConnectionNoticeResponseState(d.pop("state"))

        embedding_connection_notice_response = cls(
            code=code,
            id=id,
            intervention_required=intervention_required,
            lane=lane,
            opened_at=opened_at,
            recovered_at=recovered_at,
            state=state,
        )

        embedding_connection_notice_response.additional_properties = d
        return embedding_connection_notice_response

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
