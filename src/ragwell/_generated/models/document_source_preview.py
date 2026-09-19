from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.source_coordinate_kind import SourceCoordinateKind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.structural_unit import StructuralUnit


T = TypeVar("T", bound="DocumentSourcePreview")


@_attrs_define
class DocumentSourcePreview:
    character_count: int
    content: str
    coordinate_kind: SourceCoordinateKind
    end_offset: int
    generation_id: UUID
    next_offset: int | None
    page_number: int | None
    source_id: UUID
    source_ordinal: int
    start_offset: int
    units: list[StructuralUnit] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        character_count = self.character_count

        content = self.content

        coordinate_kind = self.coordinate_kind.value

        end_offset = self.end_offset

        generation_id = str(self.generation_id)

        next_offset: int | None
        next_offset = self.next_offset

        page_number: int | None
        page_number = self.page_number

        source_id = str(self.source_id)

        source_ordinal = self.source_ordinal

        start_offset = self.start_offset

        units: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.units, Unset):
            units = []
            for units_item_data in self.units:
                units_item = units_item_data.to_dict()
                units.append(units_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "character_count": character_count,
                "content": content,
                "coordinate_kind": coordinate_kind,
                "end_offset": end_offset,
                "generation_id": generation_id,
                "next_offset": next_offset,
                "page_number": page_number,
                "source_id": source_id,
                "source_ordinal": source_ordinal,
                "start_offset": start_offset,
            }
        )
        if units is not UNSET:
            field_dict["units"] = units

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.structural_unit import StructuralUnit

        d = dict(src_dict)
        character_count = d.pop("character_count")

        content = d.pop("content")

        coordinate_kind = SourceCoordinateKind(d.pop("coordinate_kind"))

        end_offset = d.pop("end_offset")

        generation_id = UUID(d.pop("generation_id"))

        def _parse_next_offset(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        next_offset = _parse_next_offset(d.pop("next_offset"))

        def _parse_page_number(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        page_number = _parse_page_number(d.pop("page_number"))

        source_id = UUID(d.pop("source_id"))

        source_ordinal = d.pop("source_ordinal")

        start_offset = d.pop("start_offset")

        _units = d.pop("units", UNSET)
        units: list[StructuralUnit] | Unset = UNSET
        if _units is not UNSET:
            units = []
            for units_item_data in _units:
                units_item = StructuralUnit.from_dict(units_item_data)

                units.append(units_item)

        document_source_preview = cls(
            character_count=character_count,
            content=content,
            coordinate_kind=coordinate_kind,
            end_offset=end_offset,
            generation_id=generation_id,
            next_offset=next_offset,
            page_number=page_number,
            source_id=source_id,
            source_ordinal=source_ordinal,
            start_offset=start_offset,
            units=units,
        )

        document_source_preview.additional_properties = d
        return document_source_preview

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
