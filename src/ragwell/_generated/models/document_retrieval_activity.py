from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_chunk_activity import DocumentChunkActivity


T = TypeVar("T", bound="DocumentRetrievalActivity")


@_attrs_define
class DocumentRetrievalActivity:
    chunk_appearances: int
    corpus_searches: int
    coverage_started_at: datetime.datetime
    document_scoped_searches: int
    last_returned_at: datetime.datetime | None
    measured_at: datetime.datetime
    returned_searches: int
    top_chunks: list[DocumentChunkActivity]
    window_started_at: datetime.datetime
    retention_days: int | Unset = 30
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chunk_appearances = self.chunk_appearances

        corpus_searches = self.corpus_searches

        coverage_started_at = self.coverage_started_at.isoformat()

        document_scoped_searches = self.document_scoped_searches

        last_returned_at: None | str
        if isinstance(self.last_returned_at, datetime.datetime):
            last_returned_at = self.last_returned_at.isoformat()
        else:
            last_returned_at = self.last_returned_at

        measured_at = self.measured_at.isoformat()

        returned_searches = self.returned_searches

        top_chunks = []
        for top_chunks_item_data in self.top_chunks:
            top_chunks_item = top_chunks_item_data.to_dict()
            top_chunks.append(top_chunks_item)

        window_started_at = self.window_started_at.isoformat()

        retention_days = self.retention_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "chunk_appearances": chunk_appearances,
                "corpus_searches": corpus_searches,
                "coverage_started_at": coverage_started_at,
                "document_scoped_searches": document_scoped_searches,
                "last_returned_at": last_returned_at,
                "measured_at": measured_at,
                "returned_searches": returned_searches,
                "top_chunks": top_chunks,
                "window_started_at": window_started_at,
            }
        )
        if retention_days is not UNSET:
            field_dict["retention_days"] = retention_days

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_chunk_activity import DocumentChunkActivity

        d = dict(src_dict)
        chunk_appearances = d.pop("chunk_appearances")

        corpus_searches = d.pop("corpus_searches")

        coverage_started_at = datetime.datetime.fromisoformat(
            d.pop("coverage_started_at")
        )

        document_scoped_searches = d.pop("document_scoped_searches")

        def _parse_last_returned_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_returned_at_type_0 = datetime.datetime.fromisoformat(data)

                return last_returned_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        last_returned_at = _parse_last_returned_at(d.pop("last_returned_at"))

        measured_at = datetime.datetime.fromisoformat(d.pop("measured_at"))

        returned_searches = d.pop("returned_searches")

        top_chunks = []
        _top_chunks = d.pop("top_chunks")
        for top_chunks_item_data in _top_chunks:
            top_chunks_item = DocumentChunkActivity.from_dict(top_chunks_item_data)

            top_chunks.append(top_chunks_item)

        window_started_at = datetime.datetime.fromisoformat(d.pop("window_started_at"))

        retention_days = d.pop("retention_days", UNSET)

        document_retrieval_activity = cls(
            chunk_appearances=chunk_appearances,
            corpus_searches=corpus_searches,
            coverage_started_at=coverage_started_at,
            document_scoped_searches=document_scoped_searches,
            last_returned_at=last_returned_at,
            measured_at=measured_at,
            returned_searches=returned_searches,
            top_chunks=top_chunks,
            window_started_at=window_started_at,
            retention_days=retention_days,
        )

        document_retrieval_activity.additional_properties = d
        return document_retrieval_activity

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
