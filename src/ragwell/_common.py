"""Shared validation, pagination, and bounded file helpers."""

from __future__ import annotations

import asyncio
import hashlib
import io
import os
import re
import tempfile
from collections.abc import AsyncIterator, Iterable, Iterator, Mapping
from pathlib import Path
from types import TracebackType
from typing import Any, BinaryIO, Self, TypeAlias
from urllib.parse import urlsplit
from uuid import UUID, uuid4

import httpx

from .errors import ConfigurationError

UploadInput: TypeAlias = str | os.PathLike[str] | bytes | BinaryIO
_IDEMPOTENCY_RE = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
_MEDIA_BY_SUFFIX = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
}
SUPPORTED_MEDIA_TYPES = frozenset(_MEDIA_BY_SUFFIX.values())


def resolve_configuration(
    *, base_url: str | None, api_key: str | None
) -> tuple[httpx.URL, str]:
    resolved_base = base_url if base_url is not None else os.getenv("RAGWELL_BASE_URL")
    resolved_key = api_key if api_key is not None else os.getenv("RAGWELL_API_KEY")
    if not resolved_base:
        raise ConfigurationError(
            "Set base_url or RAGWELL_BASE_URL; the beta SDK has no default endpoint"
        )
    if not resolved_key or not resolved_key.strip():
        raise ConfigurationError("Set api_key or RAGWELL_API_KEY")
    parts = urlsplit(resolved_base)
    if parts.scheme not in {"https", "http"} or not parts.hostname:
        raise ConfigurationError("base_url must be an absolute HTTP(S) URL")
    if parts.username is not None or parts.password is not None:
        raise ConfigurationError("base_url must not contain credentials")
    if parts.query or parts.fragment:
        raise ConfigurationError("base_url must not contain a query or fragment")
    if parts.scheme == "http" and parts.hostname not in {
        "localhost",
        "127.0.0.1",
        "::1",
    }:
        raise ConfigurationError("Plain HTTP is allowed only for loopback development")
    return httpx.URL(resolved_base.rstrip("/")), resolved_key.strip()


def resource_id(value: UUID | str, name: str) -> UUID:
    if isinstance(value, UUID):
        return value
    try:
        return UUID(value)
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError(f"{name} must be a UUID") from exc


def idempotency_key(value: str | None) -> str:
    key = value if value is not None else f"rw_{uuid4()}"
    if not _IDEMPOTENCY_RE.fullmatch(key):
        raise ValueError(
            "idempotency_key must be 8-128 characters from A-Z, a-z, 0-9, . _ : -"
        )
    return key


def _query_value(value: Any) -> str | int | float | bool | None:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "value"):
        return _query_value(value.value)
    return str(value)


def query_params(**values: Any) -> list[tuple[str, str | int | float | bool | None]]:
    result: list[tuple[str, str | int | float | bool | None]] = []
    for name, value in values.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple, set, frozenset)):
            result.extend((name, _query_value(item)) for item in value)
        else:
            result.append((name, _query_value(value)))
    return result


def metadata_dict(value: Any) -> Mapping[str, Any]:
    if hasattr(value, "to_dict"):
        result = value.to_dict()
        if isinstance(result, dict):
            return result
    if isinstance(value, Mapping):
        return value
    raise TypeError("request body must be a generated model or mapping")


class PreparedUpload:
    """Seekable upload content whose original cursor/ownership are preserved."""

    def __init__(
        self,
        *,
        stream: BinaryIO,
        owned: bool,
        start: int,
        filename: str,
        media_type: str,
        size: int,
        sha256: str,
    ) -> None:
        self.stream = stream
        self.owned = owned
        self.start = start
        self.filename = filename
        self.media_type = media_type
        self.size = size
        self.sha256 = sha256

    def rewind(self) -> None:
        self.stream.seek(self.start)

    def close(self) -> None:
        if self.owned:
            self.stream.close()
        else:
            self.stream.seek(self.start)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


class AsyncFileContent(httpx.AsyncByteStream):
    """Read a caller-owned seekable stream without blocking the event loop."""

    def __init__(self, stream: BinaryIO, *, chunk_size: int = 1024 * 1024) -> None:
        self.stream = stream
        self.chunk_size = chunk_size

    async def __aiter__(self) -> AsyncIterator[bytes]:
        while True:
            chunk = await asyncio.to_thread(self.stream.read, self.chunk_size)
            if not chunk:
                return
            yield chunk


class SyncFileContent(httpx.SyncByteStream):
    """Read a caller-owned stream in fixed-size chunks."""

    def __init__(self, stream: BinaryIO, *, chunk_size: int = 1024 * 1024) -> None:
        self.stream = stream
        self.chunk_size = chunk_size

    def __iter__(self) -> Iterator[bytes]:
        while True:
            chunk = self.stream.read(self.chunk_size)
            if not chunk:
                return
            yield chunk


def prepare_upload(
    source: UploadInput,
    *,
    filename: str | None,
    media_type: str | None,
    chunk_size: int = 1024 * 1024,
) -> PreparedUpload:
    owned = False
    if isinstance(source, bytes):
        if not filename:
            raise ValueError("filename is required when uploading bytes")
        stream: BinaryIO = io.BytesIO(source)
        owned = True
        start = 0
        resolved_filename = filename
    elif isinstance(source, (str, os.PathLike)):
        path = Path(source)
        stream = path.open("rb")
        owned = True
        start = 0
        resolved_filename = filename or path.name
    else:
        stream = source
        if not filename:
            raise ValueError("filename is required when uploading a file object")
        if not stream.seekable():
            raise ValueError(
                "high-level upload requires a seekable stream; use uploads.upload_content "
                "with declared metadata for a bounded non-seekable source"
            )
        try:
            start = stream.tell()
        except (OSError, ValueError) as exc:
            raise ValueError("upload stream must expose a stable cursor") from exc
        resolved_filename = filename

    suffix = Path(resolved_filename).suffix.lower()
    resolved_media = media_type or _MEDIA_BY_SUFFIX.get(suffix)
    if resolved_media not in SUPPORTED_MEDIA_TYPES:
        if owned:
            stream.close()
        raise ValueError(
            "media_type must be application/pdf, text/plain, or text/markdown"
        )

    digest = hashlib.sha256()
    size = 0
    try:
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            if not isinstance(chunk, bytes):
                raise TypeError("upload stream must be opened in binary mode")
            size += len(chunk)
            digest.update(chunk)
        stream.seek(start)
    except BaseException:
        if owned:
            stream.close()
        else:
            try:
                stream.seek(start)
            except (OSError, ValueError):
                pass
        raise
    return PreparedUpload(
        stream=stream,
        owned=owned,
        start=start,
        filename=resolved_filename,
        media_type=resolved_media,
        size=size,
        sha256=digest.hexdigest(),
    )


def create_temporary_destination(
    destination: Path, *, overwrite: bool
) -> tuple[BinaryIO, Path]:
    destination = destination.expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not overwrite:
        raise FileExistsError(destination)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".part",
    )
    return os.fdopen(descriptor, "wb"), Path(temporary_name)


def remove_temporary(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def finalize_temporary(temporary: Path, destination: Path, *, overwrite: bool) -> None:
    if destination.exists() and not overwrite:
        raise FileExistsError(destination)
    os.replace(temporary, destination)


def repeated_cursor(cursor: object, seen: set[object]) -> bool:
    if cursor is None:
        return False
    if cursor in seen:
        return True
    seen.add(cursor)
    return False


def as_uuid_list(values: Iterable[UUID | str] | None) -> list[UUID] | None:
    if values is None:
        return None
    return [resource_id(value, "document_id") for value in values]


__all__ = [
    "AsyncFileContent",
    "PreparedUpload",
    "SUPPORTED_MEDIA_TYPES",
    "SyncFileContent",
    "UploadInput",
    "as_uuid_list",
    "create_temporary_destination",
    "finalize_temporary",
    "idempotency_key",
    "metadata_dict",
    "prepare_upload",
    "query_params",
    "remove_temporary",
    "repeated_cursor",
    "resolve_configuration",
    "resource_id",
]
