"""Synchronous search using an existing granted project."""

from __future__ import annotations

import os

from ragwell import Ragwell
from ragwell.types import SearchResponse


def search(client: Ragwell, project_id: str, query: str) -> SearchResponse:
    return client.project(project_id).search(query=query)


def main() -> None:
    with Ragwell() as client:
        result = search(client, os.environ["RAGWELL_PROJECT_ID"], "retention policy")
        for item in result.items:
            print(item.rank, item.source_filename)


if __name__ == "__main__":
    main()
