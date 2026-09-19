"""Maintained HTTPX transport with bounded retries and redacted failures."""

from __future__ import annotations

import datetime as dt
import email.utils
import random
import time
from collections.abc import AsyncIterator, Callable, Iterator, Mapping, Sequence
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from types import TracebackType
from typing import Any, Literal, Protocol, Self, TypeVar, cast

import httpx

from ._generated.models import ErrorResponse, FieldError, PlanLimitErrorResponse
from ._generated.types import Unset
from .errors import (
    ApiError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ProtocolError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    TransportError,
    TransportTimeout,
    ValidationError,
)

RetryMode = Literal["none", "read", "replayable"]
ParamValue = str | int | float | bool | None
Params = (
    Mapping[str, ParamValue | Sequence[ParamValue]]
    | list[tuple[str, ParamValue]]
    | tuple[tuple[str, ParamValue], ...]
    | None
)
_MAX_ERROR_BYTES = 1_048_576
_MAX_JSON_BYTES = 16_777_216
_TRANSIENT_CODES = {"command_in_progress", "rate_limited", "temporarily_unavailable"}
_TRANSIENT_STATUSES = {502, 503, 504}


class GeneratedModel(Protocol):
    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self: ...


ModelT = TypeVar("ModelT", bound=GeneratedModel)


def _request_id(response: httpx.Response) -> str | None:
    value = response.headers.get("X-Request-ID")
    return value[:256] if value else None


def _retry_after(response: httpx.Response) -> float | None:
    value = response.headers.get("Retry-After")
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            retry_at = email.utils.parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=dt.UTC)
            return max(0.0, (retry_at - dt.datetime.now(dt.UTC)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None


def _safe_json(response: httpx.Response, *, operation_id: str) -> Mapping[str, Any]:
    content = response.content
    if len(content) > _MAX_JSON_BYTES:
        raise ProtocolError(
            "Response exceeded the SDK's bounded JSON limit",
            operation_id=operation_id,
        )
    try:
        value = response.json()
    except ValueError as exc:
        raise ProtocolError(
            "Response was not valid JSON for the documented operation",
            operation_id=operation_id,
        ) from exc
    if not isinstance(value, dict):
        raise ProtocolError(
            "Response JSON was not an object for the documented operation",
            operation_id=operation_id,
        )
    return cast(Mapping[str, Any], value)


def parse_model(
    response: httpx.Response, model_type: type[ModelT], *, operation_id: str
) -> ModelT:
    data = _safe_json(response, operation_id=operation_id)
    try:
        return model_type.from_dict(data)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise ProtocolError(
            "Response did not match the reviewed API schema",
            operation_id=operation_id,
        ) from exc


def _api_error(response: httpx.Response, *, operation_id: str) -> ApiError:
    request_id = _request_id(response)
    retry_after = _retry_after(response)
    code = f"http_{response.status_code}"
    message = "The API rejected the request"
    field_errors: tuple[FieldError, ...] = ()
    quota = None

    if len(response.content) <= _MAX_ERROR_BYTES:
        try:
            data = response.json()
            if isinstance(data, dict) and isinstance(data.get("error"), dict):
                detail = cast(dict[str, Any], data["error"])
                if "limit_key" in detail and "unit" in detail:
                    parsed_quota = PlanLimitErrorResponse.from_dict(data)
                    quota = parsed_quota.error
                    raw_code = quota.code
                    code = raw_code.value if not isinstance(raw_code, Unset) else code
                    message = quota.message
                    raw_fields = quota.field_errors
                else:
                    parsed = ErrorResponse.from_dict(data)
                    code = parsed.error.code
                    message = parsed.error.message
                    raw_fields = parsed.error.field_errors
                if not isinstance(raw_fields, Unset):
                    field_errors = tuple(raw_fields)
        except (KeyError, TypeError, ValueError, AttributeError):
            # Proxies and interrupted upstreams may return non-contract content.
            pass

    error_type: type[ApiError]
    if quota is not None or code.startswith("plan_limit_"):
        error_type = QuotaExceededError
    elif response.status_code == 401:
        error_type = AuthenticationError
    elif response.status_code == 403:
        error_type = PermissionDeniedError
    elif response.status_code == 404:
        error_type = NotFoundError
    elif response.status_code == 409:
        error_type = ConflictError
    elif response.status_code == 422:
        error_type = ValidationError
    elif response.status_code == 429:
        error_type = RateLimitError
    elif response.status_code >= 500:
        error_type = ServerError
    else:
        error_type = ApiError

    return error_type(
        status_code=response.status_code,
        code=code,
        message=message,
        operation_id=operation_id,
        request_id=request_id,
        field_errors=field_errors,
        retry_after=retry_after,
        quota=quota,
    )


def _retryable(error: ApiError) -> bool:
    if isinstance(error, QuotaExceededError):
        return False
    return error.status_code in _TRANSIENT_STATUSES or (
        error.status_code == 429 and error.code in _TRANSIENT_CODES
    )


def _delay(attempt: int, error: ApiError | None) -> float:
    if error is not None and error.retry_after is not None:
        return error.retry_after
    return float(random.random() * min(2.0, 0.25 * (2**attempt)))


def _timeout(remaining: float) -> httpx.Timeout:
    bounded = max(0.001, remaining)
    return httpx.Timeout(
        timeout=min(30.0, bounded),
        connect=min(5.0, bounded),
        pool=min(5.0, bounded),
    )


def _prepare_request(request: httpx.Request, api_key: str | None) -> None:
    request.headers.pop("cookie", None)
    request.headers.pop("x-csrf-token", None)
    if api_key is None:
        request.headers.pop("authorization", None)
    else:
        request.headers["Authorization"] = f"Bearer {api_key}"
    request.headers["User-Agent"] = "ragwell-python/0.1.0.dev0"


class SyncByteStream(AbstractContextManager["SyncByteStream"]):
    """One-shot streamed response. The caller owns it until closed."""

    def __init__(self, response: httpx.Response) -> None:
        self._response = response
        self.request_id = _request_id(response)
        self.headers = response.headers

    def iter_bytes(self, chunk_size: int = 64 * 1024) -> Iterator[bytes]:
        yield from self._response.iter_bytes(chunk_size=chunk_size)

    def close(self) -> None:
        self._response.close()

    def __enter__(self) -> SyncByteStream:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


class AsyncByteStream(AbstractAsyncContextManager["AsyncByteStream"]):
    """One-shot asynchronous streamed response. The caller owns it until closed."""

    def __init__(self, response: httpx.Response) -> None:
        self._response = response
        self.request_id = _request_id(response)
        self.headers = response.headers

    async def iter_bytes(self, chunk_size: int = 64 * 1024) -> AsyncIterator[bytes]:
        async for chunk in self._response.aiter_bytes(chunk_size=chunk_size):
            yield chunk

    async def aclose(self) -> None:
        await self._response.aclose()

    async def __aenter__(self) -> AsyncByteStream:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()


class SyncTransport:
    def __init__(
        self,
        *,
        base_url: httpx.URL,
        api_key: str,
        client: httpx.Client,
        owns_client: bool,
        operation_timeout: float,
        transfer_timeout: float,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.client = client
        self.owns_client = owns_client
        self.operation_timeout = operation_timeout
        self.transfer_timeout = transfer_timeout
        self.monotonic = monotonic
        self.sleep = sleep

    def _url(self, path: str) -> str:
        return str(self.base_url.copy_with(path=self.base_url.path.rstrip("/") + path))

    def close(self) -> None:
        if self.owns_client:
            self.client.close()

    def request(
        self,
        *,
        operation_id: str,
        method: str,
        path: str,
        model_type: type[ModelT],
        expected_statuses: set[int],
        params: Params = None,
        json: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        content: bytes | Any = None,
        retry_mode: RetryMode = "none",
        transfer: bool = False,
        before_attempt: Callable[[], None] | None = None,
        authenticated: bool = True,
    ) -> ModelT:
        response = self._send(
            operation_id=operation_id,
            method=method,
            path=path,
            expected_statuses=expected_statuses,
            params=params,
            json=json,
            headers=headers,
            content=content,
            retry_mode=retry_mode,
            transfer=transfer,
            before_attempt=before_attempt,
            authenticated=authenticated,
            stream=False,
        )
        try:
            return parse_model(response, model_type, operation_id=operation_id)
        finally:
            response.close()

    def stream(
        self,
        *,
        operation_id: str,
        path: str,
        params: Params = None,
    ) -> SyncByteStream:
        response = self._send(
            operation_id=operation_id,
            method="GET",
            path=path,
            expected_statuses={200},
            params=params,
            retry_mode="read",
            transfer=True,
            stream=True,
        )
        return SyncByteStream(response)

    def _send(
        self,
        *,
        operation_id: str,
        method: str,
        path: str,
        expected_statuses: set[int],
        params: Params = None,
        json: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        content: bytes | Any = None,
        retry_mode: RetryMode,
        transfer: bool,
        before_attempt: Callable[[], None] | None = None,
        stream: bool,
        authenticated: bool = True,
    ) -> httpx.Response:
        deadline = self.monotonic() + (
            self.transfer_timeout if transfer else self.operation_timeout
        )
        max_attempts = 3 if retry_mode != "none" else 1
        last_timeout = False
        for attempt in range(max_attempts):
            remaining = deadline - self.monotonic()
            if remaining <= 0:
                raise TransportTimeout(
                    "The operation deadline elapsed", operation_id=operation_id
                )
            if before_attempt is not None:
                before_attempt()
            request = self.client.build_request(
                method,
                self._url(path),
                params=params,
                json=json,
                headers=headers,
                content=content,
                timeout=_timeout(remaining),
            )
            _prepare_request(request, self.api_key if authenticated else None)
            try:
                response = self.client.send(
                    request, stream=stream, follow_redirects=False
                )
            except httpx.TimeoutException:
                last_timeout = True
                if attempt + 1 >= max_attempts:
                    break
                wait = _delay(attempt, None)
                if wait >= deadline - self.monotonic():
                    break
                self.sleep(wait)
                continue
            except httpx.TransportError:
                if attempt + 1 >= max_attempts:
                    raise TransportError(
                        "The HTTP transport could not complete the request",
                        operation_id=operation_id,
                    ) from None
                wait = _delay(attempt, None)
                if wait >= deadline - self.monotonic():
                    raise TransportError(
                        "The HTTP transport could not complete the request",
                        operation_id=operation_id,
                    ) from None
                self.sleep(wait)
                continue
            if response.status_code in expected_statuses:
                return response
            if stream:
                response.read()
            error = _api_error(response, operation_id=operation_id)
            response.close()
            if attempt + 1 >= max_attempts or not _retryable(error):
                raise error
            wait = _delay(attempt, error)
            if wait >= deadline - self.monotonic():
                raise error
            self.sleep(wait)
        if last_timeout:
            raise TransportTimeout(
                "The HTTP transport timed out before the operation completed",
                operation_id=operation_id,
            )
        raise TransportError(
            "The HTTP transport could not complete the request",
            operation_id=operation_id,
        )


class AsyncTransport:
    def __init__(
        self,
        *,
        base_url: httpx.URL,
        api_key: str,
        client: httpx.AsyncClient,
        owns_client: bool,
        operation_timeout: float,
        transfer_timeout: float,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Any] | None = None,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.client = client
        self.owns_client = owns_client
        self.operation_timeout = operation_timeout
        self.transfer_timeout = transfer_timeout
        self.monotonic = monotonic
        self._sleep = sleep

    def _url(self, path: str) -> str:
        return str(self.base_url.copy_with(path=self.base_url.path.rstrip("/") + path))

    async def sleep(self, delay: float) -> None:
        if self._sleep is not None:
            result = self._sleep(delay)
            if hasattr(result, "__await__"):
                await result
            return
        import asyncio

        await asyncio.sleep(delay)

    async def close(self) -> None:
        if self.owns_client:
            await self.client.aclose()

    async def request(
        self,
        *,
        operation_id: str,
        method: str,
        path: str,
        model_type: type[ModelT],
        expected_statuses: set[int],
        params: Params = None,
        json: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        content: bytes | Any = None,
        retry_mode: RetryMode = "none",
        transfer: bool = False,
        before_attempt: Callable[[], None] | None = None,
        authenticated: bool = True,
    ) -> ModelT:
        response = await self._send(
            operation_id=operation_id,
            method=method,
            path=path,
            expected_statuses=expected_statuses,
            params=params,
            json=json,
            headers=headers,
            content=content,
            retry_mode=retry_mode,
            transfer=transfer,
            before_attempt=before_attempt,
            authenticated=authenticated,
            stream=False,
        )
        try:
            return parse_model(response, model_type, operation_id=operation_id)
        finally:
            await response.aclose()

    async def stream(
        self,
        *,
        operation_id: str,
        path: str,
        params: Params = None,
    ) -> AsyncByteStream:
        response = await self._send(
            operation_id=operation_id,
            method="GET",
            path=path,
            expected_statuses={200},
            params=params,
            retry_mode="read",
            transfer=True,
            stream=True,
        )
        return AsyncByteStream(response)

    async def _send(
        self,
        *,
        operation_id: str,
        method: str,
        path: str,
        expected_statuses: set[int],
        params: Params = None,
        json: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        content: bytes | Any = None,
        retry_mode: RetryMode,
        transfer: bool,
        before_attempt: Callable[[], None] | None = None,
        stream: bool,
        authenticated: bool = True,
    ) -> httpx.Response:
        deadline = self.monotonic() + (
            self.transfer_timeout if transfer else self.operation_timeout
        )
        max_attempts = 3 if retry_mode != "none" else 1
        last_timeout = False
        for attempt in range(max_attempts):
            remaining = deadline - self.monotonic()
            if remaining <= 0:
                raise TransportTimeout(
                    "The operation deadline elapsed", operation_id=operation_id
                )
            if before_attempt is not None:
                before_attempt()
            request = self.client.build_request(
                method,
                self._url(path),
                params=params,
                json=json,
                headers=headers,
                content=content,
                timeout=_timeout(remaining),
            )
            _prepare_request(request, self.api_key if authenticated else None)
            try:
                response = await self.client.send(
                    request, stream=stream, follow_redirects=False
                )
            except httpx.TimeoutException:
                last_timeout = True
                if attempt + 1 >= max_attempts:
                    break
                wait = _delay(attempt, None)
                if wait >= deadline - self.monotonic():
                    break
                await self.sleep(wait)
                continue
            except httpx.TransportError:
                if attempt + 1 >= max_attempts:
                    raise TransportError(
                        "The HTTP transport could not complete the request",
                        operation_id=operation_id,
                    ) from None
                wait = _delay(attempt, None)
                if wait >= deadline - self.monotonic():
                    raise TransportError(
                        "The HTTP transport could not complete the request",
                        operation_id=operation_id,
                    ) from None
                await self.sleep(wait)
                continue
            if response.status_code in expected_statuses:
                return response
            if stream:
                await response.aread()
            error = _api_error(response, operation_id=operation_id)
            await response.aclose()
            if attempt + 1 >= max_attempts or not _retryable(error):
                raise error
            wait = _delay(attempt, error)
            if wait >= deadline - self.monotonic():
                raise error
            await self.sleep(wait)
        if last_timeout:
            raise TransportTimeout(
                "The HTTP transport timed out before the operation completed",
                operation_id=operation_id,
            )
        raise TransportError(
            "The HTTP transport could not complete the request",
            operation_id=operation_id,
        )


__all__ = [
    "AsyncByteStream",
    "AsyncTransport",
    "SyncByteStream",
    "SyncTransport",
]
