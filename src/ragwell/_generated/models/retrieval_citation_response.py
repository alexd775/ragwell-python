from __future__ import annotations

from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RetrievalCitationResponse")


@_attrs_define
class RetrievalCitationResponse:
    end_offset: int
    kind: Literal["page"]
    page_number: int
    source_filename: str
    start_offset: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        end_offset = self.end_offset

        kind = self.kind

        page_number = self.page_number

        source_filename = self.source_filename

        start_offset = self.start_offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "end_offset": end_offset,
                "kind": kind,
                "page_number": page_number,
                "source_filename": source_filename,
                "start_offset": start_offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        end_offset = d.pop("end_offset")

        kind = cast(Literal["page"], d.pop("kind"))
        if kind != "page":
            raise ValueError(f"kind must match const 'page', got '{kind}'")

        page_number = d.pop("page_number")

        source_filename = d.pop("source_filename")

        start_offset = d.pop("start_offset")

        retrieval_citation_response = cls(
            end_offset=end_offset,
            kind=kind,
            page_number=page_number,
            source_filename=source_filename,
            start_offset=start_offset,
        )

        retrieval_citation_response.additional_properties = d
        return retrieval_citation_response

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
