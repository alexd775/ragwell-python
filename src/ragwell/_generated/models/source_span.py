from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="SourceSpan")


@_attrs_define
class SourceSpan:
    end_offset: int
    source_ordinal: int
    start_offset: int
    block_id: None | str | Unset = UNSET
    column: int | None | Unset = UNSET
    region: list[float] | None | Unset = UNSET
    row: int | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        end_offset = self.end_offset

        source_ordinal = self.source_ordinal

        start_offset = self.start_offset

        block_id: None | str | Unset
        if isinstance(self.block_id, Unset):
            block_id = UNSET
        else:
            block_id = self.block_id

        column: int | None | Unset
        if isinstance(self.column, Unset):
            column = UNSET
        else:
            column = self.column

        region: list[float] | None | Unset
        if isinstance(self.region, Unset):
            region = UNSET
        elif isinstance(self.region, list):
            region = []
            for region_type_0_item_data in self.region:
                region_type_0_item: float
                region_type_0_item = region_type_0_item_data
                region.append(region_type_0_item)

        else:
            region = self.region

        row: int | None | Unset
        if isinstance(self.row, Unset):
            row = UNSET
        else:
            row = self.row

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "end_offset": end_offset,
                "source_ordinal": source_ordinal,
                "start_offset": start_offset,
            }
        )
        if block_id is not UNSET:
            field_dict["block_id"] = block_id
        if column is not UNSET:
            field_dict["column"] = column
        if region is not UNSET:
            field_dict["region"] = region
        if row is not UNSET:
            field_dict["row"] = row

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        end_offset = d.pop("end_offset")

        source_ordinal = d.pop("source_ordinal")

        start_offset = d.pop("start_offset")

        def _parse_block_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        block_id = _parse_block_id(d.pop("block_id", UNSET))

        def _parse_column(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        column = _parse_column(d.pop("column", UNSET))

        def _parse_region(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                region_type_0 = []
                _region_type_0 = data
                for region_type_0_item_data in _region_type_0:

                    def _parse_region_type_0_item(data: object) -> float:
                        return cast(float, data)

                    region_type_0_item = _parse_region_type_0_item(
                        region_type_0_item_data
                    )

                    region_type_0.append(region_type_0_item)

                return region_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        region = _parse_region(d.pop("region", UNSET))

        def _parse_row(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        row = _parse_row(d.pop("row", UNSET))

        source_span = cls(
            end_offset=end_offset,
            source_ordinal=source_ordinal,
            start_offset=start_offset,
            block_id=block_id,
            column=column,
            region=region,
            row=row,
        )

        return source_span
