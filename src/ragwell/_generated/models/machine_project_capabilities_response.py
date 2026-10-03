from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

from ..models.grantable_api_key_scope import GrantableApiKeyScope

T = TypeVar("T", bound="MachineProjectCapabilitiesResponse")


@_attrs_define
class MachineProjectCapabilitiesResponse:
    project_id: UUID
    scopes: list[GrantableApiKeyScope]

    def to_dict(self) -> dict[str, Any]:
        project_id = str(self.project_id)

        scopes = []
        for scopes_item_data in self.scopes:
            scopes_item = scopes_item_data.value
            scopes.append(scopes_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "project_id": project_id,
                "scopes": scopes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project_id = UUID(d.pop("project_id"))

        scopes = []
        _scopes = d.pop("scopes")
        for scopes_item_data in _scopes:
            scopes_item = GrantableApiKeyScope(scopes_item_data)

            scopes.append(scopes_item)

        machine_project_capabilities_response = cls(
            project_id=project_id,
            scopes=scopes,
        )

        return machine_project_capabilities_response
