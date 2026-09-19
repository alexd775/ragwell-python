from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_chunk_page import DocumentChunkPage
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: UUID,
    document_id: UUID,
    generation_id: UUID,
    *,
    limit: int | Unset = 25,
    after: int | None | Unset = UNSET,
    text: None | str | Unset = UNSET,
    source_ordinal: int | None | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    json_after: int | None | Unset
    if isinstance(after, Unset):
        json_after = UNSET
    else:
        json_after = after
    params["after"] = json_after

    json_text: None | str | Unset
    if isinstance(text, Unset):
        json_text = UNSET
    else:
        json_text = text
    params["text"] = json_text

    json_source_ordinal: int | None | Unset
    if isinstance(source_ordinal, Unset):
        json_source_ordinal = UNSET
    else:
        json_source_ordinal = source_ordinal
    params["source_ordinal"] = json_source_ordinal

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/projects/{project_id}/documents/{document_id}/generations/{generation_id}/chunks".format(
            project_id=quote(str(project_id), safe=""),
            document_id=quote(str(document_id), safe=""),
            generation_id=quote(str(generation_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DocumentChunkPage | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = DocumentChunkPage.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = ErrorResponse.from_dict(response.json())

        return response_403

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404

    if response.status_code == 409:
        response_409 = ErrorResponse.from_dict(response.json())

        return response_409

    if response.status_code == 422:
        response_422 = ErrorResponse.from_dict(response.json())

        return response_422

    if response.status_code == 429:
        response_429 = ErrorResponse.from_dict(response.json())

        return response_429

    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500

    if response.status_code == 503:
        response_503 = ErrorResponse.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DocumentChunkPage | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: UUID,
    document_id: UUID,
    generation_id: UUID,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 25,
    after: int | None | Unset = UNSET,
    text: None | str | Unset = UNSET,
    source_ordinal: int | None | Unset = UNSET,
) -> Response[DocumentChunkPage | ErrorResponse]:
    """List Document Chunks

    Args:
        project_id (UUID):
        document_id (UUID):
        generation_id (UUID):
        limit (int | Unset):  Default: 25.
        after (int | None | Unset):
        text (None | str | Unset):
        source_ordinal (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentChunkPage | ErrorResponse]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        document_id=document_id,
        generation_id=generation_id,
        limit=limit,
        after=after,
        text=text,
        source_ordinal=source_ordinal,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: UUID,
    document_id: UUID,
    generation_id: UUID,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 25,
    after: int | None | Unset = UNSET,
    text: None | str | Unset = UNSET,
    source_ordinal: int | None | Unset = UNSET,
) -> DocumentChunkPage | ErrorResponse | None:
    """List Document Chunks

    Args:
        project_id (UUID):
        document_id (UUID):
        generation_id (UUID):
        limit (int | Unset):  Default: 25.
        after (int | None | Unset):
        text (None | str | Unset):
        source_ordinal (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentChunkPage | ErrorResponse
    """

    return sync_detailed(
        project_id=project_id,
        document_id=document_id,
        generation_id=generation_id,
        client=client,
        limit=limit,
        after=after,
        text=text,
        source_ordinal=source_ordinal,
    ).parsed


async def asyncio_detailed(
    project_id: UUID,
    document_id: UUID,
    generation_id: UUID,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 25,
    after: int | None | Unset = UNSET,
    text: None | str | Unset = UNSET,
    source_ordinal: int | None | Unset = UNSET,
) -> Response[DocumentChunkPage | ErrorResponse]:
    """List Document Chunks

    Args:
        project_id (UUID):
        document_id (UUID):
        generation_id (UUID):
        limit (int | Unset):  Default: 25.
        after (int | None | Unset):
        text (None | str | Unset):
        source_ordinal (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentChunkPage | ErrorResponse]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        document_id=document_id,
        generation_id=generation_id,
        limit=limit,
        after=after,
        text=text,
        source_ordinal=source_ordinal,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: UUID,
    document_id: UUID,
    generation_id: UUID,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 25,
    after: int | None | Unset = UNSET,
    text: None | str | Unset = UNSET,
    source_ordinal: int | None | Unset = UNSET,
) -> DocumentChunkPage | ErrorResponse | None:
    """List Document Chunks

    Args:
        project_id (UUID):
        document_id (UUID):
        generation_id (UUID):
        limit (int | Unset):  Default: 25.
        after (int | None | Unset):
        text (None | str | Unset):
        source_ordinal (int | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentChunkPage | ErrorResponse
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            document_id=document_id,
            generation_id=generation_id,
            client=client,
            limit=limit,
            after=after,
            text=text,
            source_ordinal=source_ordinal,
        )
    ).parsed
