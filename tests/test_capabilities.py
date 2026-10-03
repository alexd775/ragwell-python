"""Discovery failures must not broaden access or become metered probes."""

import asyncio

import httpx
import pytest

from ragwell import AsyncRagwell, Ragwell
from ragwell.errors import AuthenticationError, NotFoundError


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "status,error", [(401, AuthenticationError), (404, NotFoundError)]
)
def test_discovery_failure_is_typed_with_no_fallback(
    asynchronous: bool, status: int, error: type[Exception]
) -> None:
    calls: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            status,
            json={"error": {"code": "unavailable", "message": "Unavailable"}},
        )

    async def exercise() -> None:
        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(respond),
        ) as client:
            with pytest.raises(error):
                await client.capabilities.get()

    if asynchronous:
        asyncio.run(exercise())
    else:
        with Ragwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(respond),
        ) as client:
            with pytest.raises(error):
                client.capabilities.get()
    assert len(calls) == 1
    assert calls[0].method == "GET"
    assert calls[0].url.path == "/v1/machine/capabilities"
    assert not calls[0].url.query
    assert calls[0].headers["Authorization"] == "Bearer test-key"
    assert "Cookie" not in calls[0].headers
