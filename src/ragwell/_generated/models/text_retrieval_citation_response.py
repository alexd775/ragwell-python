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

T = TypeVar("T", bound="TextRetrievalCitationResponse")


@_attrs_define
class TextRetrievalCitationResponse:
    end_line: int
    end_offset: int
    kind: Literal["text"]
    source_filename: str
    start_line: int
    start_offset: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        end_line = self.end_line

        end_offset = self.end_offset

        kind = self.kind

        source_filename = self.source_filename

        start_line = self.start_line

        start_offset = self.start_offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "end_line": end_line,
                "end_offset": end_offset,
                "kind": kind,
                "source_filename": source_filename,
                "start_line": start_line,
                "start_offset": start_offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        end_line = d.pop("end_line")

        end_offset = d.pop("end_offset")

        kind = cast(Literal["text"], d.pop("kind"))
        if kind != "text":
            raise ValueError(f"kind must match const 'text', got '{kind}'")

        source_filename = d.pop("source_filename")

        start_line = d.pop("start_line")

        start_offset = d.pop("start_offset")

        text_retrieval_citation_response = cls(
            end_line=end_line,
            end_offset=end_offset,
            kind=kind,
            source_filename=source_filename,
            start_line=start_line,
            start_offset=start_offset,
        )

        text_retrieval_citation_response.additional_properties = d
        return text_retrieval_citation_response

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
