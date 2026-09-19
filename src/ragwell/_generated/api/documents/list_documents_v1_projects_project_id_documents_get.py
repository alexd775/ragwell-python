from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_list_response import DocumentListResponse
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: UUID,
    *,
    limit: int | Unset = 50,
    document_ids: list[UUID] | Unset = UNSET,
    tags_any: list[str] | Unset = UNSET,
    tags_all: list[str] | Unset = UNSET,
    source_any: list[str] | Unset = UNSET,
    author_any: list[str] | Unset = UNSET,
    language_any: list[str] | Unset = UNSET,
    category_any: list[str] | Unset = UNSET,
    after: None | Unset | UUID = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    json_document_ids: list[str] | Unset = UNSET
    if not isinstance(document_ids, Unset):
        json_document_ids = []
        for document_ids_item_data in document_ids:
            document_ids_item = str(document_ids_item_data)
            json_document_ids.append(document_ids_item)

    params["document_ids"] = json_document_ids

    json_tags_any: list[str] | Unset = UNSET
    if not isinstance(tags_any, Unset):
        json_tags_any = tags_any

    params["tags_any"] = json_tags_any

    json_tags_all: list[str] | Unset = UNSET
    if not isinstance(tags_all, Unset):
        json_tags_all = tags_all

    params["tags_all"] = json_tags_all

    json_source_any: list[str] | Unset = UNSET
    if not isinstance(source_any, Unset):
        json_source_any = source_any

    params["source_any"] = json_source_any

    json_author_any: list[str] | Unset = UNSET
    if not isinstance(author_any, Unset):
        json_author_any = author_any

    params["author_any"] = json_author_any

    json_language_any: list[str] | Unset = UNSET
    if not isinstance(language_any, Unset):
        json_language_any = language_any

    params["language_any"] = json_language_any

    json_category_any: list[str] | Unset = UNSET
    if not isinstance(category_any, Unset):
        json_category_any = category_any

    params["category_any"] = json_category_any

    json_after: None | str | Unset
    if isinstance(after, Unset):
        json_after = UNSET
    elif isinstance(after, UUID):
        json_after = str(after)
    else:
        json_after = after
    params["after"] = json_after

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/projects/{project_id}/documents".format(
            project_id=quote(str(project_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DocumentListResponse | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = DocumentListResponse.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404

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
) -> Response[DocumentListResponse | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: UUID,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
    document_ids: list[UUID] | Unset = UNSET,
    tags_any: list[str] | Unset = UNSET,
    tags_all: list[str] | Unset = UNSET,
    source_any: list[str] | Unset = UNSET,
    author_any: list[str] | Unset = UNSET,
    language_any: list[str] | Unset = UNSET,
    category_any: list[str] | Unset = UNSET,
    after: None | Unset | UUID = UNSET,
) -> Response[DocumentListResponse | ErrorResponse]:
    """List Documents

    Args:
        project_id (UUID):
        limit (int | Unset):  Default: 50.
        document_ids (list[UUID] | Unset):
        tags_any (list[str] | Unset):
        tags_all (list[str] | Unset):
        source_any (list[str] | Unset):
        author_any (list[str] | Unset):
        language_any (list[str] | Unset):
        category_any (list[str] | Unset):
        after (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentListResponse | ErrorResponse]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        limit=limit,
        document_ids=document_ids,
        tags_any=tags_any,
        tags_all=tags_all,
        source_any=source_any,
        author_any=author_any,
        language_any=language_any,
        category_any=category_any,
        after=after,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: UUID,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
    document_ids: list[UUID] | Unset = UNSET,
    tags_any: list[str] | Unset = UNSET,
    tags_all: list[str] | Unset = UNSET,
    source_any: list[str] | Unset = UNSET,
    author_any: list[str] | Unset = UNSET,
    language_any: list[str] | Unset = UNSET,
    category_any: list[str] | Unset = UNSET,
    after: None | Unset | UUID = UNSET,
) -> DocumentListResponse | ErrorResponse | None:
    """List Documents

    Args:
        project_id (UUID):
        limit (int | Unset):  Default: 50.
        document_ids (list[UUID] | Unset):
        tags_any (list[str] | Unset):
        tags_all (list[str] | Unset):
        source_any (list[str] | Unset):
        author_any (list[str] | Unset):
        language_any (list[str] | Unset):
        category_any (list[str] | Unset):
        after (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentListResponse | ErrorResponse
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
        limit=limit,
        document_ids=document_ids,
        tags_any=tags_any,
        tags_all=tags_all,
        source_any=source_any,
        author_any=author_any,
        language_any=language_any,
        category_any=category_any,
        after=after,
    ).parsed


async def asyncio_detailed(
    project_id: UUID,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
    document_ids: list[UUID] | Unset = UNSET,
    tags_any: list[str] | Unset = UNSET,
    tags_all: list[str] | Unset = UNSET,
    source_any: list[str] | Unset = UNSET,
    author_any: list[str] | Unset = UNSET,
    language_any: list[str] | Unset = UNSET,
    category_any: list[str] | Unset = UNSET,
    after: None | Unset | UUID = UNSET,
) -> Response[DocumentListResponse | ErrorResponse]:
    """List Documents

    Args:
        project_id (UUID):
        limit (int | Unset):  Default: 50.
        document_ids (list[UUID] | Unset):
        tags_any (list[str] | Unset):
        tags_all (list[str] | Unset):
        source_any (list[str] | Unset):
        author_any (list[str] | Unset):
        language_any (list[str] | Unset):
        category_any (list[str] | Unset):
        after (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentListResponse | ErrorResponse]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        limit=limit,
        document_ids=document_ids,
        tags_any=tags_any,
        tags_all=tags_all,
        source_any=source_any,
        author_any=author_any,
        language_any=language_any,
        category_any=category_any,
        after=after,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: UUID,
    *,
    client: AuthenticatedClient,
    limit: int | Unset = 50,
    document_ids: list[UUID] | Unset = UNSET,
    tags_any: list[str] | Unset = UNSET,
    tags_all: list[str] | Unset = UNSET,
    source_any: list[str] | Unset = UNSET,
    author_any: list[str] | Unset = UNSET,
    language_any: list[str] | Unset = UNSET,
    category_any: list[str] | Unset = UNSET,
    after: None | Unset | UUID = UNSET,
) -> DocumentListResponse | ErrorResponse | None:
    """List Documents

    Args:
        project_id (UUID):
        limit (int | Unset):  Default: 50.
        document_ids (list[UUID] | Unset):
        tags_any (list[str] | Unset):
        tags_all (list[str] | Unset):
        source_any (list[str] | Unset):
        author_any (list[str] | Unset):
        language_any (list[str] | Unset):
        category_any (list[str] | Unset):
        after (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentListResponse | ErrorResponse
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
            limit=limit,
            document_ids=document_ids,
            tags_any=tags_any,
            tags_all=tags_all,
            source_any=source_any,
            author_any=author_any,
            language_any=language_any,
            category_any=category_any,
            after=after,
        )
    ).parsed
