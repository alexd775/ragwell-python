from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.structural_unit_kind import StructuralUnitKind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.source_span import SourceSpan


T = TypeVar("T", bound="StructuralUnit")


@_attrs_define
class StructuralUnit:
    kind: StructuralUnitKind
    span: SourceSpan
    cells: list[SourceSpan] | Unset = UNSET
    headers: list[SourceSpan] | Unset = UNSET
    headings: list[SourceSpan] | Unset = UNSET
    section: str | Unset = "root"
    sentences: list[SourceSpan] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        span = self.span.to_dict()

        cells: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.cells, Unset):
            cells = []
            for cells_item_data in self.cells:
                cells_item = cells_item_data.to_dict()
                cells.append(cells_item)

        headers: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.headers, Unset):
            headers = []
            for headers_item_data in self.headers:
                headers_item = headers_item_data.to_dict()
                headers.append(headers_item)

        headings: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.headings, Unset):
            headings = []
            for headings_item_data in self.headings:
                headings_item = headings_item_data.to_dict()
                headings.append(headings_item)

        section = self.section

        sentences: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.sentences, Unset):
            sentences = []
            for sentences_item_data in self.sentences:
                sentences_item = sentences_item_data.to_dict()
                sentences.append(sentences_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "kind": kind,
                "span": span,
            }
        )
        if cells is not UNSET:
            field_dict["cells"] = cells
        if headers is not UNSET:
            field_dict["headers"] = headers
        if headings is not UNSET:
            field_dict["headings"] = headings
        if section is not UNSET:
            field_dict["section"] = section
        if sentences is not UNSET:
            field_dict["sentences"] = sentences

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.source_span import SourceSpan

        d = dict(src_dict)
        kind = StructuralUnitKind(d.pop("kind"))

        span = SourceSpan.from_dict(d.pop("span"))

        _cells = d.pop("cells", UNSET)
        cells: list[SourceSpan] | Unset = UNSET
        if _cells is not UNSET:
            cells = []
            for cells_item_data in _cells:
                cells_item = SourceSpan.from_dict(cells_item_data)

                cells.append(cells_item)

        _headers = d.pop("headers", UNSET)
        headers: list[SourceSpan] | Unset = UNSET
        if _headers is not UNSET:
            headers = []
            for headers_item_data in _headers:
                headers_item = SourceSpan.from_dict(headers_item_data)

                headers.append(headers_item)

        _headings = d.pop("headings", UNSET)
        headings: list[SourceSpan] | Unset = UNSET
        if _headings is not UNSET:
            headings = []
            for headings_item_data in _headings:
                headings_item = SourceSpan.from_dict(headings_item_data)

                headings.append(headings_item)

        section = d.pop("section", UNSET)

        _sentences = d.pop("sentences", UNSET)
        sentences: list[SourceSpan] | Unset = UNSET
        if _sentences is not UNSET:
            sentences = []
            for sentences_item_data in _sentences:
                sentences_item = SourceSpan.from_dict(sentences_item_data)

                sentences.append(sentences_item)

        structural_unit = cls(
            kind=kind,
            span=span,
            cells=cells,
            headers=headers,
            headings=headings,
            section=section,
            sentences=sentences,
        )

        return structural_unit
