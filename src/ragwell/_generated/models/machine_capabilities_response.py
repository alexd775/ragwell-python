from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.machine_project_capabilities_response import (
        MachineProjectCapabilitiesResponse,
    )


T = TypeVar("T", bound="MachineCapabilitiesResponse")


@_attrs_define
class MachineCapabilitiesResponse:
    projects: list[MachineProjectCapabilitiesResponse]

    def to_dict(self) -> dict[str, Any]:
        projects = []
        for projects_item_data in self.projects:
            projects_item = projects_item_data.to_dict()
            projects.append(projects_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "projects": projects,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.machine_project_capabilities_response import (
            MachineProjectCapabilitiesResponse,
        )

        d = dict(src_dict)
        projects = []
        _projects = d.pop("projects")
        for projects_item_data in _projects:
            projects_item = MachineProjectCapabilitiesResponse.from_dict(
                projects_item_data
            )

            projects.append(projects_item)

        machine_capabilities_response = cls(
            projects=projects,
        )

        return machine_capabilities_response
