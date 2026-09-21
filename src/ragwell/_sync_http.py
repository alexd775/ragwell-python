"""HTTPX adapter with remaining-budget timeouts at each synchronous socket call.

HTTPX exposes inactivity timeouts. HTTPCore's public network-backend interface
lets the SDK clip them again as a request progresses, including trickled headers.
No worker thread continues a timed-out HTTP mutation in the background.
"""

from __future__ import annotations

import ssl
from collections.abc import Iterable, Iterator
from contextvars import ContextVar
from typing import Any
from urllib.request import getproxies, proxy_bypass

import httpcore
import httpx

from ._deadline import Deadline, DeadlineScope

_CURRENT: ContextVar[Deadline | None] = ContextVar(
    "ragwell_socket_deadline", default=None
)


def network_budget(budget: Deadline) -> DeadlineScope:
    return DeadlineScope(_CURRENT, budget)


def _timeout(timeout: float | None) -> float | None:
    budget = _CURRENT.get()
    if budget is None:
        return timeout
    remaining = budget.remaining()
    return remaining if timeout is None else min(timeout, remaining)


class DeadlineStream(httpcore.NetworkStream):
    def __init__(self, stream: httpcore.NetworkStream) -> None:
        self.stream = stream

    def read(self, max_bytes: int, timeout: float | None = None) -> bytes:
        data = self.stream.read(min(max_bytes, 65536), timeout=_timeout(timeout))
        _timeout(timeout)
        return data

    def write(self, buffer: bytes, timeout: float | None = None) -> None:
        for start in range(0, len(buffer), 65536):
            self.stream.write(buffer[start : start + 65536], timeout=_timeout(timeout))
        _timeout(timeout)

    def close(self) -> None:
        self.stream.close()

    def start_tls(
        self,
        ssl_context: ssl.SSLContext,
        server_hostname: str | None = None,
        timeout: float | None = None,
    ) -> httpcore.NetworkStream:
        stream = self.stream.start_tls(
            ssl_context, server_hostname=server_hostname, timeout=_timeout(timeout)
        )
        try:
            _timeout(timeout)
        except BaseException:
            stream.close()
            raise
        return DeadlineStream(stream)

    def get_extra_info(self, info: str) -> Any:
        return self.stream.get_extra_info(info)


class DeadlineBackend(httpcore.NetworkBackend):
    def __init__(self, backend: httpcore.NetworkBackend | None = None) -> None:
        self.backend = backend if backend is not None else httpcore.SyncBackend()

    def connect_tcp(
        self,
        host: str,
        port: int,
        timeout: float | None = None,
        local_address: str | None = None,
        socket_options: Iterable[httpcore.SOCKET_OPTION] | None = None,
    ) -> httpcore.NetworkStream:
        stream = self.backend.connect_tcp(
            host,
            port,
            timeout=_timeout(timeout),
            local_address=local_address,
            socket_options=socket_options,
        )
        try:
            _timeout(timeout)
        except BaseException:
            stream.close()
            raise
        return DeadlineStream(stream)

    def connect_unix_socket(
        self,
        path: str,
        timeout: float | None = None,
        socket_options: Iterable[httpcore.SOCKET_OPTION] | None = None,
    ) -> httpcore.NetworkStream:
        stream = self.backend.connect_unix_socket(
            path, timeout=_timeout(timeout), socket_options=socket_options
        )
        try:
            _timeout(timeout)
        except BaseException:
            stream.close()
            raise
        return DeadlineStream(stream)


def _httpx_error(error: Exception) -> httpx.TransportError:
    if isinstance(error, httpcore.TimeoutException):
        return httpx.TimeoutException("HTTP transport timeout")
    return httpx.TransportError("HTTP transport failure")


_CORE_ERRORS = (
    httpcore.TimeoutException,
    httpcore.NetworkError,
    httpcore.ProtocolError,
    httpcore.ProxyError,
    httpcore.UnsupportedProtocol,
)


class _ResponseBody(httpx.SyncByteStream):
    def __init__(self, response: httpcore.Response) -> None:
        self.response = response

    def __iter__(self) -> Iterator[bytes]:
        try:
            yield from self.response.iter_stream()
        except _CORE_ERRORS as error:
            raise _httpx_error(error) from None

    def close(self) -> None:
        try:
            self.response.close()
        except _CORE_ERRORS as error:
            raise _httpx_error(error) from None


class DeadlineHTTPTransport(httpx.BaseTransport):
    def __init__(
        self,
        base_url: httpx.URL,
        *,
        verify: bool,
        backend: httpcore.NetworkBackend | None = None,
    ) -> None:
        context = httpx.create_ssl_context(verify=verify)
        network = DeadlineBackend(backend)
        # The SDK has one configured origin. Retain ordinary environment proxy
        # selection even though HTTPX disables automatic mounts for custom transports.
        proxies = getproxies()
        proxy_url = (
            None
            if proxy_bypass(base_url.host)
            else proxies.get(base_url.scheme, proxies.get("all"))
        )
        self.pool: httpcore.ConnectionPool
        if proxy_url:
            proxy = httpx.Proxy(proxy_url)
            self.pool = httpcore.HTTPProxy(
                proxy_url=str(proxy.url),
                proxy_auth=proxy.raw_auth,
                proxy_headers=proxy.headers.raw,
                proxy_ssl_context=proxy.ssl_context,
                ssl_context=context,
                network_backend=network,
                max_connections=100,
                max_keepalive_connections=20,
                keepalive_expiry=5.0,
            )
        else:
            self.pool = httpcore.ConnectionPool(
                ssl_context=context,
                network_backend=network,
                max_connections=100,
                max_keepalive_connections=20,
                keepalive_expiry=5.0,
            )

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        assert isinstance(request.stream, httpx.SyncByteStream)
        core_request = httpcore.Request(
            method=request.method,
            url=httpcore.URL(
                scheme=request.url.raw_scheme,
                host=request.url.raw_host,
                port=request.url.port,
                target=request.url.raw_path,
            ),
            headers=request.headers.raw,
            content=request.stream,
            extensions=request.extensions,
        )
        try:
            response = self.pool.handle_request(core_request)
        except _CORE_ERRORS as error:
            raise _httpx_error(error) from None
        return httpx.Response(
            response.status,
            headers=response.headers,
            stream=_ResponseBody(response),
            extensions=response.extensions,
        )

    def close(self) -> None:
        self.pool.close()
