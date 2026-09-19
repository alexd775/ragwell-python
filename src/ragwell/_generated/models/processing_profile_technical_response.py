from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ProcessingProfileTechnicalResponse")


@_attrs_define
class ProcessingProfileTechnicalResponse:
    boundary_behavior: str
    chunk_max_characters: int
    chunk_max_tokens: int | None
    chunk_min_tokens: int
    chunk_overlap_characters: int
    chunk_overlap_tokens: int
    chunker: str
    distance_metric: str
    embedding_dimensions: int
    embedding_model: str
    embedding_provider: str
    extractor: str
    extractor_version: str
    normalization: str
    representation_version: str
    retrieval_version: str
    tokenizer: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        boundary_behavior = self.boundary_behavior

        chunk_max_characters = self.chunk_max_characters

        chunk_max_tokens: int | None
        chunk_max_tokens = self.chunk_max_tokens

        chunk_min_tokens = self.chunk_min_tokens

        chunk_overlap_characters = self.chunk_overlap_characters

        chunk_overlap_tokens = self.chunk_overlap_tokens

        chunker = self.chunker

        distance_metric = self.distance_metric

        embedding_dimensions = self.embedding_dimensions

        embedding_model = self.embedding_model

        embedding_provider = self.embedding_provider

        extractor = self.extractor

        extractor_version = self.extractor_version

        normalization = self.normalization

        representation_version = self.representation_version

        retrieval_version = self.retrieval_version

        tokenizer = self.tokenizer

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "boundary_behavior": boundary_behavior,
                "chunk_max_characters": chunk_max_characters,
                "chunk_max_tokens": chunk_max_tokens,
                "chunk_min_tokens": chunk_min_tokens,
                "chunk_overlap_characters": chunk_overlap_characters,
                "chunk_overlap_tokens": chunk_overlap_tokens,
                "chunker": chunker,
                "distance_metric": distance_metric,
                "embedding_dimensions": embedding_dimensions,
                "embedding_model": embedding_model,
                "embedding_provider": embedding_provider,
                "extractor": extractor,
                "extractor_version": extractor_version,
                "normalization": normalization,
                "representation_version": representation_version,
                "retrieval_version": retrieval_version,
                "tokenizer": tokenizer,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        boundary_behavior = d.pop("boundary_behavior")

        chunk_max_characters = d.pop("chunk_max_characters")

        def _parse_chunk_max_tokens(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        chunk_max_tokens = _parse_chunk_max_tokens(d.pop("chunk_max_tokens"))

        chunk_min_tokens = d.pop("chunk_min_tokens")

        chunk_overlap_characters = d.pop("chunk_overlap_characters")

        chunk_overlap_tokens = d.pop("chunk_overlap_tokens")

        chunker = d.pop("chunker")

        distance_metric = d.pop("distance_metric")

        embedding_dimensions = d.pop("embedding_dimensions")

        embedding_model = d.pop("embedding_model")

        embedding_provider = d.pop("embedding_provider")

        extractor = d.pop("extractor")

        extractor_version = d.pop("extractor_version")

        normalization = d.pop("normalization")

        representation_version = d.pop("representation_version")

        retrieval_version = d.pop("retrieval_version")

        tokenizer = d.pop("tokenizer")

        processing_profile_technical_response = cls(
            boundary_behavior=boundary_behavior,
            chunk_max_characters=chunk_max_characters,
            chunk_max_tokens=chunk_max_tokens,
            chunk_min_tokens=chunk_min_tokens,
            chunk_overlap_characters=chunk_overlap_characters,
            chunk_overlap_tokens=chunk_overlap_tokens,
            chunker=chunker,
            distance_metric=distance_metric,
            embedding_dimensions=embedding_dimensions,
            embedding_model=embedding_model,
            embedding_provider=embedding_provider,
            extractor=extractor,
            extractor_version=extractor_version,
            normalization=normalization,
            representation_version=representation_version,
            retrieval_version=retrieval_version,
            tokenizer=tokenizer,
        )

        processing_profile_technical_response.additional_properties = d
        return processing_profile_technical_response

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
