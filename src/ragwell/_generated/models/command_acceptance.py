from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.command_acceptance_operation import CommandAcceptanceOperation

T = TypeVar("T", bound="CommandAcceptance")


@_attrs_define
class CommandAcceptance:
    accepted_at: datetime.datetime
    applied_revision: int | None
    expires_at: datetime.datetime
    id: UUID
    operation: CommandAcceptanceOperation
    replayed: bool
    result_id: UUID
    retry_request_count: int | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        accepted_at = self.accepted_at.isoformat()

        applied_revision: int | None
        applied_revision = self.applied_revision

        expires_at = self.expires_at.isoformat()

        id = str(self.id)

        operation = self.operation.value

        replayed = self.replayed

        result_id = str(self.result_id)

        retry_request_count: int | None
        retry_request_count = self.retry_request_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accepted_at": accepted_at,
                "applied_revision": applied_revision,
                "expires_at": expires_at,
                "id": id,
                "operation": operation,
                "replayed": replayed,
                "result_id": result_id,
                "retry_request_count": retry_request_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        accepted_at = datetime.datetime.fromisoformat(d.pop("accepted_at"))

        def _parse_applied_revision(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        applied_revision = _parse_applied_revision(d.pop("applied_revision"))

        expires_at = datetime.datetime.fromisoformat(d.pop("expires_at"))

        id = UUID(d.pop("id"))

        operation = CommandAcceptanceOperation(d.pop("operation"))

        replayed = d.pop("replayed")

        result_id = UUID(d.pop("result_id"))

        def _parse_retry_request_count(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        retry_request_count = _parse_retry_request_count(d.pop("retry_request_count"))

        command_acceptance = cls(
            accepted_at=accepted_at,
            applied_revision=applied_revision,
            expires_at=expires_at,
            id=id,
            operation=operation,
            replayed=replayed,
            result_id=result_id,
            retry_request_count=retry_request_count,
        )

        command_acceptance.additional_properties = d
        return command_acceptance

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
