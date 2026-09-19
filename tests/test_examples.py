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
