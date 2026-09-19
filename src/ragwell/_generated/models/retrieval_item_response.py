from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.chunk_part import ChunkPart
    from ..models.retrieval_citation_response import RetrievalCitationResponse
    from ..models.retrieval_scores_response import RetrievalScoresResponse
    from ..models.text_retrieval_citation_response import TextRetrievalCitationResponse


T = TypeVar("T", bound="RetrievalItemResponse")


@_attrs_define
class RetrievalItemResponse:
    chunk_id: UUID
    citation: None | RetrievalCitationResponse | TextRetrievalCitationResponse
    content: str
    document_id: UUID
    document_version_id: UUID
    parts: list[ChunkPart]
    rank: int
    representation_version: str
    scores: RetrievalScoresResponse
    source_filename: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.retrieval_citation_response import RetrievalCitationResponse
        from ..models.text_retrieval_citation_response import (
            TextRetrievalCitationResponse,
        )

        chunk_id = str(self.chunk_id)

        citation: dict[str, Any] | None
        if isinstance(self.citation, RetrievalCitationResponse):
            citation = self.citation.to_dict()
        elif isinstance(self.citation, TextRetrievalCitationResponse):
            citation = self.citation.to_dict()
        else:
            citation = self.citation

        content = self.content

        document_id = str(self.document_id)

        document_version_id = str(self.document_version_id)

        parts = []
        for parts_item_data in self.parts:
            parts_item = parts_item_data.to_dict()
            parts.append(parts_item)

        rank = self.rank

        representation_version = self.representation_version

        scores = self.scores.to_dict()

        source_filename = self.source_filename

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "chunk_id": chunk_id,
                "citation": citation,
                "content": content,
                "document_id": document_id,
                "document_version_id": document_version_id,
                "parts": parts,
                "rank": rank,
                "representation_version": representation_version,
                "scores": scores,
                "source_filename": source_filename,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chunk_part import ChunkPart
        from ..models.retrieval_citation_response import RetrievalCitationResponse
        from ..models.retrieval_scores_response import RetrievalScoresResponse
        from ..models.text_retrieval_citation_response import (
            TextRetrievalCitationResponse,
        )

        d = dict(src_dict)
        chunk_id = UUID(d.pop("chunk_id"))

        def _parse_citation(
            data: object,
        ) -> None | RetrievalCitationResponse | TextRetrievalCitationResponse:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                citation_type_0_type_0 = RetrievalCitationResponse.from_dict(data)

                return citation_type_0_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                citation_type_0_type_1 = TextRetrievalCitationResponse.from_dict(data)

                return citation_type_0_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None | RetrievalCitationResponse | TextRetrievalCitationResponse, data
            )

        citation = _parse_citation(d.pop("citation"))

        content = d.pop("content")

        document_id = UUID(d.pop("document_id"))

        document_version_id = UUID(d.pop("document_version_id"))

        parts = []
        _parts = d.pop("parts")
        for parts_item_data in _parts:
            parts_item = ChunkPart.from_dict(parts_item_data)

            parts.append(parts_item)

        rank = d.pop("rank")

        representation_version = d.pop("representation_version")

        scores = RetrievalScoresResponse.from_dict(d.pop("scores"))

        source_filename = d.pop("source_filename")

        retrieval_item_response = cls(
            chunk_id=chunk_id,
            citation=citation,
            content=content,
            document_id=document_id,
            document_version_id=document_version_id,
            parts=parts,
            rank=rank,
            representation_version=representation_version,
            scores=scores,
            source_filename=source_filename,
        )

        retrieval_item_response.additional_properties = d
        return retrieval_item_response

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
