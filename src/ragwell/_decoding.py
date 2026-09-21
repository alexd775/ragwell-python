"""Incremental response decoding with bounded output, including compressed bodies."""

from __future__ import annotations

import zlib
from collections.abc import Iterator

import httpx

from .errors import ProtocolError

BUFFER_SIZE = 64 * 1024


class Decoder:
    def __init__(self, response: httpx.Response, operation_id: str) -> None:
        self.operation_id = operation_id
        encoding = response.headers.get("content-encoding", "identity").lower().strip()
        # HTTPX mock/preloaded responses have already been decoded.
        if response.is_stream_consumed:
            encoding = "identity"
        if encoding not in {"identity", "gzip", "deflate"}:
            raise ProtocolError(
                "Unsupported response content encoding", operation_id=operation_id
            )
        self.encoding = encoding
        self.decoder = (
            None
            if encoding == "identity"
            else zlib.decompressobj(31 if encoding == "gzip" else 15)
        )

    def decode(self, raw: bytes) -> Iterator[bytes]:
        if self.decoder is None:
            for start in range(0, len(raw), BUFFER_SIZE):
                yield raw[start : start + BUFFER_SIZE]
            return
        try:
            while raw:
                if self.decoder.eof:
                    if self.encoding != "gzip":
                        raise zlib.error()
                    self.decoder = zlib.decompressobj(31)
                decoded = self.decoder.decompress(raw, BUFFER_SIZE)
                raw = (
                    self.decoder.unused_data
                    if self.decoder.eof
                    else self.decoder.unconsumed_tail
                )
                if decoded:
                    yield decoded
        except zlib.error:
            raise ProtocolError(
                "Invalid compressed response", operation_id=self.operation_id
            ) from None

    def finish(self) -> None:
        if self.decoder is not None and not self.decoder.eof:
            raise ProtocolError(
                "Incomplete compressed response", operation_id=self.operation_id
            )
