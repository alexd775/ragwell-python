"""Both client styles preserve explicit reranking and never replay paid searches."""

import asyncio
import json
import traceback

import httpx
import pytest

from ragwell import (
    ApiError,
    AsyncRagwell,
    ConflictError,
    ProtocolError,
    Ragwell,
    ServerError,
)
from ragwell.types import (
    UNSET,
    ChunkPartKind,
    RerankMetadata,
    RerankMetadataProvider,
    RerankParams,
    RerankRequest,
    SearchResponse,
    TextRetrievalCitationResponse,
)

from ._fixtures import (
    CHUNK_ID,
    DOCUMENT_ID,
    PROJECT_ID,
    RETRIEVAL_ID,
    SOURCE_ID,
    VERSION_ID,
)


@pytest.mark.parametrize("style", ["sync", "async"])
def test_search_reranking_omission_null_and_typed_response(style: str) -> None:
    requests = []

    def handle(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        requests.append(body)
        assert request.headers["Authorization"] == "Bearer ragwell-test-key"
        return httpx.Response(
            200,
            json={
                "retrieval_id": RETRIEVAL_ID,
                "retrieval_version": "hybrid-v1+jev-relevance-v1",
                "profile_id": "profile-v1",
                "items": [
                    {
                        "rank": 1,
                        "chunk_id": CHUNK_ID,
                        "document_id": DOCUMENT_ID,
                        "document_version_id": VERSION_ID,
                        "content": "Refunds are available for 30 days.",
                        "source_filename": "policy.txt",
                        "representation_version": "rep-v1",
                        "parts": [
                            {
                                "kind": "evidence",
                                "text": "Refunds are available for 30 days.",
                                "source_id": SOURCE_ID,
                                "start_line": 4,
                                "end_line": 4,
                            }
                        ],
                        "citation": {
                            "kind": "text",
                            "source_filename": "policy.txt",
                            "start_line": 4,
                            "end_line": 4,
                            "start_offset": 0,
                            "end_offset": 34,
                        },
                        "scores": {
                            "text": 0.4,
                            "vector": 0.7,
                            "hybrid": 0.65,
                            "rerank": 2.75,
                            "rerank_confidence": 0.88,
                            "final": 2.75,
                        },
                    }
                ]
                if body.get("rerank")
                else [],
                "rerank": {
                    "id": "jev",
                    "model": "~typesafe/jev-latest",
                    "provider": "openrouter",
                    "resolved_model": "jev-1.13.0",
                    "policy": "jev-relevance-v1",
                    "configuration_revision": 3,
                    "applied": True,
                    "candidate_count": 1,
                }
                if body.get("rerank")
                else None,
            },
        )

    options = [UNSET, None, RerankRequest(id="jev", params=RerankParams())]
    if style == "sync":
        with Ragwell(
            base_url="https://api.example.test",
            api_key="ragwell-test-key",
            transport=httpx.MockTransport(handle),
        ) as client:
            for option in options:
                result = client.project(PROJECT_ID).search(
                    query="refund policy", rerank=option
                )
    else:

        async def run() -> SearchResponse:
            async with AsyncRagwell(
                base_url="https://api.example.test",
                api_key="ragwell-test-key",
                transport=httpx.MockTransport(handle),
            ) as client:
                for option in options:
                    result = await client.project(PROJECT_ID).search(
                        query="refund policy", rerank=option
                    )
                return result

        result = asyncio.run(run())
    assert "rerank" not in requests[0]
    assert requests[1]["rerank"] is None
    assert requests[2]["rerank"] == {"id": "jev", "params": {}}
    assert isinstance(result.rerank, RerankMetadata)
    assert result.rerank.configuration_revision == 3
    assert result.rerank.applied is True
    assert result.rerank.provider is RerankMetadataProvider.OPENROUTER
    assert result.rerank.model == "~typesafe/jev-latest"
    assert result.rerank.resolved_model == "jev-1.13.0"
    assert len(result.items) == 1
    item = result.items[0]
    assert item.rank == 1
    assert item.scores.hybrid == pytest.approx(0.65)
    assert item.scores.rerank == pytest.approx(2.75)
    assert item.scores.rerank_confidence == pytest.approx(0.88)
    assert item.scores.final == pytest.approx(2.75)
    assert item.parts[0].kind is ChunkPartKind.EVIDENCE
    assert item.parts[0].source_id is not None
    assert str(item.parts[0].source_id) == SOURCE_ID
    assert isinstance(item.citation, TextRetrievalCitationResponse)
    assert item.citation.start_line == 4


@pytest.mark.parametrize("style", ["sync", "async"])
@pytest.mark.parametrize(
    ("status", "code", "error_type"),
    [
        (409, "project_reranker_misconfigured", ConflictError),
        (503, "reranker_unavailable", ServerError),
    ],
)
def test_reranker_errors_are_preserved_without_automatic_replay(
    style: str, status: int, code: str, error_type: type[ApiError]
) -> None:
    calls = []

    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(
            status,
            json={
                "error": {
                    "code": code,
                    "message": "Check project reranker configuration.",
                }
            },
            headers={"Retry-After": "30"},
        )

    if style == "sync":
        with Ragwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(handle),
        ) as client:
            with pytest.raises(error_type) as caught:
                client.project(PROJECT_ID).search(
                    query="query", rerank=RerankRequest(id="jev")
                )
    else:

        async def run() -> pytest.ExceptionInfo[ApiError]:
            async with AsyncRagwell(
                base_url="https://api.example.test",
                api_key="test-key",
                transport=httpx.MockTransport(handle),
            ) as client:
                with pytest.raises(error_type) as caught:
                    await client.project(PROJECT_ID).search(
                        query="query", rerank=RerankRequest(id="jev")
                    )
                return caught

        caught = asyncio.run(run())
    assert caught.value.code == code
    assert len(calls) == 1


@pytest.mark.parametrize("style", ["sync", "async"])
def test_malformed_rerank_metadata_is_a_safe_protocol_error(style: str) -> None:
    marker = "synthetic-unknown-provider"

    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "retrieval_id": RETRIEVAL_ID,
                "retrieval_version": "hybrid-v1+jev-relevance-v1",
                "profile_id": "profile-v1",
                "items": [],
                "rerank": {
                    "id": "jev",
                    "model": "jev-1.13.0",
                    "provider": marker,
                    "policy": "jev-relevance-v1",
                    "configuration_revision": 3,
                    "applied": True,
                    "candidate_count": 1,
                },
            },
            headers={"X-Request-ID": "request-rerank-protocol"},
        )

    if style == "sync":
        with Ragwell(
            base_url="https://api.example.test",
            api_key="test-key",
            transport=httpx.MockTransport(handle),
        ) as client:
            with pytest.raises(ProtocolError) as caught:
                client.project(PROJECT_ID).search(
                    query="query", rerank=RerankRequest(id="jev")
                )
    else:

        async def run() -> pytest.ExceptionInfo[ProtocolError]:
            async with AsyncRagwell(
                base_url="https://api.example.test",
                api_key="test-key",
                transport=httpx.MockTransport(handle),
            ) as client:
                with pytest.raises(ProtocolError) as caught:
                    await client.project(PROJECT_ID).search(
                        query="query", rerank=RerankRequest(id="jev")
                    )
                return caught

        caught = asyncio.run(run())

    assert caught.value.operation_id == "search_v1_projects__project_id__search_post"
    assert caught.value.request_id == "request-rerank-protocol"
    assert marker not in "".join(traceback.format_exception(caught.value))
