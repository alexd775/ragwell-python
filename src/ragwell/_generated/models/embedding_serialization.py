from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="EmbeddingSerialization")


@_attrs_define
class EmbeddingSerialization:
    input_tokens: int
    serializer: str
    sha256: str
    text: str
    tokenizer_id: str

    def to_dict(self) -> dict[str, Any]:
        input_tokens = self.input_tokens

        serializer = self.serializer

        sha256 = self.sha256

        text = self.text

        tokenizer_id = self.tokenizer_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "input_tokens": input_tokens,
                "serializer": serializer,
                "sha256": sha256,
                "text": text,
                "tokenizer_id": tokenizer_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        input_tokens = d.pop("input_tokens")

        serializer = d.pop("serializer")

        sha256 = d.pop("sha256")

        text = d.pop("text")

        tokenizer_id = d.pop("tokenizer_id")

        embedding_serialization = cls(
            input_tokens=input_tokens,
            serializer=serializer,
            sha256=sha256,
            text=text,
            tokenizer_id=tokenizer_id,
        )

        return embedding_serialization
