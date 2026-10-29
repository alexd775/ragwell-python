"""Project context discovery uses the current scoped projection without search."""

import asyncio
from collections.abc import Callable
from uuid import UUID

import httpx
import pytest

from ragwell import AsyncRagwell, Ragwell
from ragwell.errors import (
    AuthenticationError,
    NotFoundError,
    PermissionDeniedError,
    ProtocolError,
)
from ragwell.types import ProjectAgentDescriptionResponse

from ._fixtures import PROJECT_ID


def call_description(
    asynchronous: bool, respond: Callable[[httpx.Request], httpx.Response]
) -> ProjectAgentDescriptionResponse:
    async def exercise() -> ProjectAgentDescriptionResponse:
        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(respond),
        ) as client:
            return await client.project(PROJECT_ID).agent_description()

    if asynchronous:
        return asyncio.run(exercise())
    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(respond),
    ) as client:
        return client.project(PROJECT_ID).agent_description()


@pytest.mark.parametrize("asynchronous", [False, True])
def test_current_description_round_trips_null_updates_and_clearing(
    asynchronous: bool,
) -> None:
    calls: list[httpx.Request] = []
    descriptions = iter([None, "Approved product policies", "Changed knowledge", None])

    def respond(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "project_id": PROJECT_ID,
                "description": next(descriptions),
                "future_field": "preserved",
            },
            headers={"Cache-Control": "no-store"},
        )

    async def exercise() -> list[str | None]:
        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(respond),
        ) as client:
            project = client.project(PROJECT_ID)
            return [(await project.agent_description()).description for _ in range(4)]

    if asynchronous:
        observed = asyncio.run(exercise())
    else:
        with Ragwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(respond),
        ) as client:
            project = client.project(PROJECT_ID)
            results = [project.agent_description() for _ in range(4)]
            observed = [result.description for result in results]
            assert results[1].project_id == UUID(PROJECT_ID)
            assert results[1].to_dict() == {
                "project_id": PROJECT_ID,
                "description": "Approved product policies",
                "future_field": "preserved",
            }
    assert observed == [None, "Approved product policies", "Changed knowledge", None]
    assert len(calls) == 4
    for request in calls:
        assert request.method == "GET"
        assert request.url.path == f"/v1/projects/{PROJECT_ID}/agent-description"
        assert not request.url.query and not request.content
        assert request.headers["Authorization"] == "Bearer test-key"
        assert "Cookie" not in request.headers


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "status,error",
    [(401, AuthenticationError), (403, PermissionDeniedError), (404, NotFoundError)],
)
def test_denial_has_no_project_list_or_search_fallback(
    asynchronous: bool, status: int, error: type[Exception]
) -> None:
    calls: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            status,
            json={"error": {"code": "unavailable", "message": "Unavailable"}},
        )

    with pytest.raises(error):
        call_description(asynchronous, respond)
    assert len(calls) == 1
    assert calls[0].url.path.endswith("/agent-description")


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "body",
    [
        {"project_id": "00000000-0000-4000-8000-000000000999", "description": "Other"},
        {"project_id": PROJECT_ID, "description": "x" * 2001},
        {"project_id": PROJECT_ID, "description": 3},
        {"project_id": PROJECT_ID},
    ],
)
def test_invalid_or_substituted_projection_fails_closed(
    asynchronous: bool, body: dict[str, object]
) -> None:
    calls: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json=body)

    with pytest.raises(ProtocolError) as failure:
        call_description(asynchronous, respond)
    assert failure.value.operation_id == "get_project_agent_description"
    assert len(calls) == 1
