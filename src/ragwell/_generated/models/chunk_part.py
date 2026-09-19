from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define

from ..models.chunk_part_kind import ChunkPartKind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.source_span import SourceSpan


T = TypeVar("T", bound="ChunkPart")


@_attrs_define
class ChunkPart:
    kind: ChunkPartKind
    text: str
    end_line: int | None | Unset = UNSET
    page_number: int | None | Unset = UNSET
    source_id: None | Unset | UUID = UNSET
    span: None | SourceSpan | Unset = UNSET
    start_line: int | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.source_span import SourceSpan

        kind = self.kind.value

        text = self.text

        end_line: int | None | Unset
        if isinstance(self.end_line, Unset):
            end_line = UNSET
        else:
            end_line = self.end_line

        page_number: int | None | Unset
        if isinstance(self.page_number, Unset):
            page_number = UNSET
        else:
            page_number = self.page_number

        source_id: None | str | Unset
        if isinstance(self.source_id, Unset):
            source_id = UNSET
        elif isinstance(self.source_id, UUID):
            source_id = str(self.source_id)
        else:
            source_id = self.source_id

        span: dict[str, Any] | None | Unset
        if isinstance(self.span, Unset):
            span = UNSET
        elif isinstance(self.span, SourceSpan):
            span = self.span.to_dict()
        else:
            span = self.span

        start_line: int | None | Unset
        if isinstance(self.start_line, Unset):
            start_line = UNSET
        else:
            start_line = self.start_line

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "text": text,
            }
        )
        if end_line is not UNSET:
            field_dict["end_line"] = end_line
        if page_number is not UNSET:
            field_dict["page_number"] = page_number
        if source_id is not UNSET:
            field_dict["source_id"] = source_id
        if span is not UNSET:
            field_dict["span"] = span
        if start_line is not UNSET:
            field_dict["start_line"] = start_line

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.source_span import SourceSpan

        d = dict(src_dict)
        kind = ChunkPartKind(d.pop("kind"))

        text = d.pop("text")

        def _parse_end_line(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        end_line = _parse_end_line(d.pop("end_line", UNSET))

        def _parse_page_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        page_number = _parse_page_number(d.pop("page_number", UNSET))

        def _parse_source_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                source_id_type_0 = UUID(data)

                return source_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        source_id = _parse_source_id(d.pop("source_id", UNSET))

        def _parse_span(data: object) -> None | SourceSpan | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                span_type_0 = SourceSpan.from_dict(data)

                return span_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SourceSpan | Unset, data)

        span = _parse_span(d.pop("span", UNSET))

        def _parse_start_line(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        start_line = _parse_start_line(d.pop("start_line", UNSET))

        chunk_part = cls(
            kind=kind,
            text=text,
            end_line=end_line,
            page_number=page_number,
            source_id=source_id,
            span=span,
            start_line=start_line,
        )

        return chunk_part
