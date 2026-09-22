"""Maintained HTTPX transport with bounded retries and redacted failures."""

from __future__ import annotations

import asyncio
import datetime as dt
import email.utils
import math
import random
import time
from collections.abc import AsyncIterator, Callable, Iterator, Mapping, Sequence
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from contextvars import ContextVar
from types import TracebackType
from typing import Any, Literal, Protocol, Self, TypeVar, cast

import httpx

from ._deadline import Deadline, DeadlineScope
from ._decoding import BUFFER_SIZE, Decoder
from ._generated.models import ErrorResponse, FieldError, PlanLimitErrorResponse
from ._generated.types import Unset
from ._sync_http import network_budget
from ._version import __version__
from .errors import (
    ApiError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ProtocolError,
    QuotaExceededError,
    RagwellError,
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
        seconds = float(value)
        return max(0.0, seconds) if math.isfinite(seconds) else None
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
    except (ValueError, RecursionError):
        raise ProtocolError(
            "Response was not valid JSON for the documented operation",
            operation_id=operation_id,
        ) from None
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
    except (
        KeyError,
        TypeError,
        ValueError,
        AttributeError,
        OverflowError,
        RecursionError,
    ):
        raise ProtocolError(
            "Response did not match the reviewed API schema",
            operation_id=operation_id,
        ) from None


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
        except (
            KeyError,
            TypeError,
            ValueError,
            AttributeError,
            OverflowError,
            RecursionError,
        ):
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
    request.headers["Accept-Encoding"] = "gzip, deflate"
    request.headers["User-Agent"] = f"ragwell-python/{__version__}"


def _annotate(error: RagwellError, response: httpx.Response) -> None:
    error.request_id = _request_id(response)


class _Budgets:
    operation_timeout: float
    transfer_timeout: float
    monotonic: Callable[[], float]

    def _initialize_budgets(self) -> None:
        self._budget: ContextVar[Deadline | None] = ContextVar(
            "ragwell_deadline", default=None
        )

    def scope(
        self,
        seconds: float,
        operation_id: str,
        *,
        error: Callable[[], RagwellError] | None = None,
    ) -> DeadlineScope:
        return DeadlineScope(
            self._budget,
            Deadline(
                seconds,
                self.monotonic,
                operation_id=operation_id,
                parent=self._budget.get(),
                error=error,
            ),
        )

    def _deadline(
        self, operation_id: str, transfer: bool, retry_mode: RetryMode
    ) -> Deadline:
        seconds = self.transfer_timeout if transfer else self.operation_timeout
        # Command receipts are guaranteed for 24h. Never replay at/after that
        # horizon even when a caller selects a much larger operation timeout.
        if retry_mode == "replayable":
            seconds = min(seconds, 24 * 60 * 60)
        return Deadline(
            seconds,
            self.monotonic,
            operation_id=operation_id,
            parent=self._budget.get(),
        )


class _SyncRequestBody(httpx.SyncByteStream):
    def __init__(self, stream: httpx.SyncByteStream, budget: Deadline) -> None:
        self.stream, self.budget = stream, budget

    def __iter__(self) -> Iterator[bytes]:
        iterator = iter(self.stream)
        while True:
            self.budget.check()
            try:
                chunk = next(iterator)
            except StopIteration:
                return
            self.budget.check()
            yield chunk


class _AsyncRequestBody(httpx.AsyncByteStream):
    def __init__(self, stream: httpx.AsyncByteStream, budget: Deadline) -> None:
        self.stream, self.budget = stream, budget

    async def __aiter__(self) -> AsyncIterator[bytes]:
        iterator = aiter(self.stream)
        while True:
            self.budget.check()
            try:
                chunk = await anext(iterator)
            except StopAsyncIteration:
                return
            self.budget.check()
            yield chunk


class SyncByteStream(AbstractContextManager["SyncByteStream"]):
    """One-shot bounded decoding stream; consume and close within its deadline."""

    def __init__(self, response: httpx.Response, budget: Deadline) -> None:
        self._response = response
        self._budget = budget
        self.request_id = _request_id(response)
        self.headers = response.headers

    def iter_bytes(self, chunk_size: int = BUFFER_SIZE) -> Iterator[bytes]:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        chunk_size = min(chunk_size, BUFFER_SIZE)
        try:
            decoder = Decoder(self._response, self._budget.operation_id)
            chunks = (
                self._response.iter_bytes(chunk_size=BUFFER_SIZE)
                if self._response.is_stream_consumed
                else self._response.iter_raw()
            )
            while True:
                self._budget.check()
                try:
                    with network_budget(self._budget):
                        raw = next(chunks)
                except StopIteration:
                    break
                self._budget.check()
                for decoded in decoder.decode(raw):
                    for start in range(0, len(decoded), chunk_size):
                        self._budget.check()
                        yield decoded[start : start + chunk_size]
            decoder.finish()
            self._budget.check()
        except (httpx.TimeoutException, TimeoutError):
            self._budget.check()
            error: TransportError = TransportTimeout(
                "The response stream timed out", operation_id=self._budget.operation_id
            )
            _annotate(error, self._response)
            raise error from None
        except httpx.HTTPError:
            error = TransportError(
                "The response stream could not be completed",
                operation_id=self._budget.operation_id,
            )
            _annotate(error, self._response)
            raise error from None
        except RagwellError as error:
            _annotate(error, self._response)
            raise
        finally:
            self.close()

    def close(self) -> None:
        try:
            self._response.close()
        except httpx.HTTPError:
            error = TransportError(
                "The response stream could not be closed",
                operation_id=self._budget.operation_id,
            )
            _annotate(error, self._response)
            raise error from None

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
    """One-shot bounded decoding stream; consume and close within its deadline."""

    def __init__(self, response: httpx.Response, budget: Deadline) -> None:
        self._response = response
        self._budget = budget
        self.request_id = _request_id(response)
        self.headers = response.headers

    async def iter_bytes(self, chunk_size: int = BUFFER_SIZE) -> AsyncIterator[bytes]:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        chunk_size = min(chunk_size, BUFFER_SIZE)
        try:
            decoder = Decoder(self._response, self._budget.operation_id)
            if self._response.is_stream_consumed:
                chunks = self._response.aiter_bytes(chunk_size=BUFFER_SIZE)
            else:
                chunks = self._response.aiter_raw()
            while True:
                self._budget.check()
                try:
                    async with asyncio.timeout(self._budget.remaining()):
                        raw = await anext(chunks)
                except StopAsyncIteration:
                    break
                self._budget.check()
                for decoded in decoder.decode(raw):
                    for start in range(0, len(decoded), chunk_size):
                        self._budget.check()
                        yield decoded[start : start + chunk_size]
            decoder.finish()
            self._budget.check()
        except (httpx.TimeoutException, TimeoutError):
            self._budget.check()
            error: TransportError = TransportTimeout(
                "The response stream timed out", operation_id=self._budget.operation_id
            )
            _annotate(error, self._response)
            raise error from None
        except httpx.HTTPError:
            error = TransportError(
                "The response stream could not be completed",
                operation_id=self._budget.operation_id,
            )
            _annotate(error, self._response)
            raise error from None
        except RagwellError as error:
            _annotate(error, self._response)
            raise
        finally:
            await self.aclose()

    async def aclose(self) -> None:
        try:
            await self._response.aclose()
        except httpx.HTTPError:
            error = TransportError(
                "The response stream could not be closed",
                operation_id=self._budget.operation_id,
            )
            _annotate(error, self._response)
            raise error from None

    async def __aenter__(self) -> AsyncByteStream:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()


class SyncTransport(_Budgets):
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
        self._initialize_budgets()

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
        validator: Callable[[ModelT], None] | None = None,
    ) -> ModelT:
        budget = self._deadline(operation_id, transfer, retry_mode)
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
            before_attempt=before_attempt,
            authenticated=authenticated,
            stream=False,
            budget=budget,
        )
        try:
            budget.check()
            result = parse_model(response, model_type, operation_id=operation_id)
            if validator is not None:
                validator(result)
            budget.check()
            return result
        except RagwellError as error:
            _annotate(error, response)
            raise
        finally:
            response.close()

    def stream(
        self, *, operation_id: str, path: str, params: Params = None
    ) -> SyncByteStream:
        budget = self._deadline(operation_id, True, "read")
        response = self._send(
            operation_id=operation_id,
            method="GET",
            path=path,
            expected_statuses={200},
            params=params,
            retry_mode="read",
            stream=True,
            budget=budget,
        )
        return SyncByteStream(response, budget)

    def _read(
        self, response: httpx.Response, budget: Deadline, limit: int
    ) -> httpx.Response:
        body = bytearray()
        stream = SyncByteStream(response, budget)
        try:
            for chunk in stream.iter_bytes():
                if len(body) + len(chunk) > limit:
                    raise ProtocolError(
                        "Response exceeded the SDK's bounded body limit",
                        operation_id=budget.operation_id,
                    )
                body.extend(chunk)
        except RagwellError as error:
            _annotate(error, response)
            raise
        finally:
            stream.close()
        # The source stream is closed. Parse only this bounded, decoded body.
        headers = response.headers.copy()
        headers.pop("content-encoding", None)
        return httpx.Response(
            response.status_code,
            headers=headers,
            content=bytes(body),
            request=response.request,
        )

    def _send(
        self,
        *,
        operation_id: str,
        method: str,
        path: str,
        expected_statuses: set[int],
        retry_mode: RetryMode,
        stream: bool,
        budget: Deadline,
        params: Params = None,
        json: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        content: bytes | Any = None,
        before_attempt: Callable[[], None] | None = None,
        authenticated: bool = True,
    ) -> httpx.Response:
        max_attempts = 3 if retry_mode != "none" else 1
        for attempt in range(max_attempts):
            budget.check()
            if before_attempt is not None:
                before_attempt()
            request = self.client.build_request(
                method,
                self._url(path),
                params=params,
                json=json,
                headers=headers,
                content=content,
                timeout=_timeout(budget.remaining()),
            )
            _prepare_request(request, self.api_key if authenticated else None)
            assert isinstance(request.stream, httpx.SyncByteStream)
            request.stream = _SyncRequestBody(request.stream, budget)
            response: httpx.Response | None = None
            error: ApiError | TransportError
            try:
                with network_budget(budget):
                    response = self.client.send(
                        request, stream=True, follow_redirects=False
                    )
                budget.request_id = _request_id(response)
                budget.check()
                success = response.status_code in expected_statuses
                if success and stream:
                    return response
                response = self._read(
                    response, budget, _MAX_JSON_BYTES if success else _MAX_ERROR_BYTES
                )
                budget.check()
                if success:
                    return response
                error = _api_error(response, operation_id=operation_id)
                response.close()
                if not _retryable(error):
                    raise error
            except (httpx.TimeoutException, TimeoutError):
                if response is not None:
                    response.close()
                budget.check()
                error = TransportTimeout(
                    "The HTTP transport timed out before the operation completed",
                    operation_id=operation_id,
                )
            except httpx.HTTPError:
                if response is not None:
                    response.close()
                error = TransportError(
                    "The HTTP transport could not complete the request",
                    operation_id=operation_id,
                )
            except TransportError as caught:
                if response is not None:
                    response.close()
                budget.check()
                error = caught
            except BaseException:
                if response is not None:
                    response.close()
                raise
            if response is not None:
                _annotate(error, response)
            budget.check()
            if attempt + 1 >= max_attempts:
                raise error from None
            wait = _delay(attempt, error if isinstance(error, ApiError) else None)
            if wait >= budget.remaining():
                raise error from None
            self.sleep(wait)
        raise AssertionError("unreachable")


class AsyncTransport(_Budgets):
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
        self._initialize_budgets()

    async def sleep(self, delay: float) -> None:
        if self._sleep is not None:
            result = self._sleep(delay)
            if hasattr(result, "__await__"):
                await result
        else:
            await asyncio.sleep(delay)

    def _url(self, path: str) -> str:
        return str(self.base_url.copy_with(path=self.base_url.path.rstrip("/") + path))

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
        validator: Callable[[ModelT], None] | None = None,
    ) -> ModelT:
        budget = self._deadline(operation_id, transfer, retry_mode)
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
            before_attempt=before_attempt,
            authenticated=authenticated,
            stream=False,
            budget=budget,
        )
        try:
            budget.check()
            result = parse_model(response, model_type, operation_id=operation_id)
            if validator is not None:
                validator(result)
            budget.check()
            return result
        except RagwellError as error:
            _annotate(error, response)
            raise
        finally:
            await response.aclose()

    async def stream(
        self, *, operation_id: str, path: str, params: Params = None
    ) -> AsyncByteStream:
        budget = self._deadline(operation_id, True, "read")
        response = await self._send(
            operation_id=operation_id,
            method="GET",
            path=path,
            expected_statuses={200},
            params=params,
            retry_mode="read",
            stream=True,
            budget=budget,
        )
        return AsyncByteStream(response, budget)

    async def _read(
        self, response: httpx.Response, budget: Deadline, limit: int
    ) -> httpx.Response:
        body = bytearray()
        stream = AsyncByteStream(response, budget)
        try:
            async for chunk in stream.iter_bytes():
                if len(body) + len(chunk) > limit:
                    raise ProtocolError(
                        "Response exceeded the SDK's bounded body limit",
                        operation_id=budget.operation_id,
                    )
                body.extend(chunk)
        except RagwellError as error:
            _annotate(error, response)
            raise
        finally:
            await stream.aclose()
        # The source stream is closed. Parse only this bounded, decoded body.
        headers = response.headers.copy()
        headers.pop("content-encoding", None)
        return httpx.Response(
            response.status_code,
            headers=headers,
            content=bytes(body),
            request=response.request,
        )

    async def _send(
        self,
        *,
        operation_id: str,
        method: str,
        path: str,
        expected_statuses: set[int],
        retry_mode: RetryMode,
        stream: bool,
        budget: Deadline,
        params: Params = None,
        json: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        content: bytes | Any = None,
        before_attempt: Callable[[], None] | None = None,
        authenticated: bool = True,
    ) -> httpx.Response:
        max_attempts = 3 if retry_mode != "none" else 1
        for attempt in range(max_attempts):
            budget.check()
            if before_attempt is not None:
                before_attempt()
            request = self.client.build_request(
                method,
                self._url(path),
                params=params,
                json=json,
                headers=headers,
                content=content,
                timeout=_timeout(budget.remaining()),
            )
            _prepare_request(request, self.api_key if authenticated else None)
            assert isinstance(request.stream, httpx.AsyncByteStream)
            request.stream = _AsyncRequestBody(request.stream, budget)
            response: httpx.Response | None = None
            error: ApiError | TransportError
            try:
                async with asyncio.timeout(budget.remaining()):
                    response = await self.client.send(
                        request, stream=True, follow_redirects=False
                    )
                budget.request_id = _request_id(response)
                budget.check()
                success = response.status_code in expected_statuses
                if success and stream:
                    return response
                response = await self._read(
                    response, budget, _MAX_JSON_BYTES if success else _MAX_ERROR_BYTES
                )
                budget.check()
                if success:
                    return response
                error = _api_error(response, operation_id=operation_id)
                await response.aclose()
                if not _retryable(error):
                    raise error
            except (httpx.TimeoutException, TimeoutError):
                if response is not None:
                    await response.aclose()
                budget.check()
                error = TransportTimeout(
                    "The HTTP transport timed out before the operation completed",
                    operation_id=operation_id,
                )
            except httpx.HTTPError:
                if response is not None:
                    await response.aclose()
                error = TransportError(
                    "The HTTP transport could not complete the request",
                    operation_id=operation_id,
                )
            except TransportError as caught:
                if response is not None:
                    await response.aclose()
                budget.check()
                error = caught
            except BaseException:
                if response is not None:
                    await response.aclose()
                raise
            if response is not None:
                _annotate(error, response)
            budget.check()
            if attempt + 1 >= max_attempts:
                raise error from None
            wait = _delay(attempt, error if isinstance(error, ApiError) else None)
            if wait >= budget.remaining():
                raise error from None
            await self.sleep(wait)
        raise AssertionError("unreachable")


__all__ = ["AsyncByteStream", "AsyncTransport", "SyncByteStream", "SyncTransport"]
