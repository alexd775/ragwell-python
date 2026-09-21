"""Execute the documented examples against deterministic synthetic HTTP."""

from __future__ import annotations

import asyncio

import httpx

from examples.async_search import search as async_search
from examples.sync_search import search as sync_search
from ragwell import AsyncRagwell, Ragwell

from ._fixtures import PROJECT_ID, RecordingAPI


def test_sync_example_executes() -> None:
    api = RecordingAPI()
    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(api.sync),
    ) as client:
        result = sync_search(client, PROJECT_ID, "synthetic")
    assert result.retrieval_version == "retrieval-v1"


def test_async_example_executes() -> None:
    async def exercise() -> None:
        api = RecordingAPI()
        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(api.async_),
        ) as client:
            result = await async_search(client, PROJECT_ID, "synthetic")
        assert result.retrieval_version == "retrieval-v1"

    asyncio.run(exercise())


def test_sync_lifecycle_example_executes() -> None:
    from examples.sync_lifecycle import lifecycle

    api = RecordingAPI()
    with Ragwell(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(api.sync),
    ) as client:
        result = lifecycle(client, PROJECT_ID)
    assert result["export_parts"] == 1
    assert result["deletion_receipt_id"]
    assert [request.method for request in api.requests].count("DELETE") == 1


def test_async_lifecycle_example_executes() -> None:
    from examples.async_lifecycle import lifecycle

    async def exercise() -> None:
        api = RecordingAPI()
        async with AsyncRagwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(api.async_),
        ) as client:
            result = await lifecycle(client, PROJECT_ID)
        assert result["export_parts"] == 1
        assert result["deletion_receipt_id"]
        assert [request.method for request in api.requests].count("DELETE") == 1

    asyncio.run(exercise())
