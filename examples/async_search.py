"""Asynchronous search using an existing granted project."""

from __future__ import annotations

import asyncio
import os

from ragwell import AsyncRagwell
from ragwell.types import SearchResponse


async def search(client: AsyncRagwell, project_id: str, query: str) -> SearchResponse:
    return await client.project(project_id).search(query=query)


async def main() -> None:
    async with AsyncRagwell() as client:
        result = await search(
            client, os.environ["RAGWELL_PROJECT_ID"], "retention policy"
        )
        for item in result.items:
            print(item.rank, item.source_filename)


if __name__ == "__main__":
    asyncio.run(main())
