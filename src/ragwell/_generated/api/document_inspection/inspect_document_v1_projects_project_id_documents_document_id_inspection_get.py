from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_inspection_response import DocumentInspectionResponse
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: UUID,
    document_id: UUID,
    *,
    generation_id: None | Unset | UUID = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_generation_id: None | str | Unset
    if isinstance(generation_id, Unset):
        json_generation_id = UNSET
    elif isinstance(generation_id, UUID):
        json_generation_id = str(generation_id)
    else:
        json_generation_id = generation_id
    params["generation_id"] = json_generation_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/projects/{project_id}/documents/{document_id}/inspection".format(
            project_id=quote(str(project_id), safe=""),
            document_id=quote(str(document_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DocumentInspectionResponse | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = DocumentInspectionResponse.from_dict(response.json())

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
) -> Response[DocumentInspectionResponse | ErrorResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: UUID,
    document_id: UUID,
    *,
    client: AuthenticatedClient,
    generation_id: None | Unset | UUID = UNSET,
) -> Response[DocumentInspectionResponse | ErrorResponse]:
    """Inspect Document

    Args:
        project_id (UUID):
        document_id (UUID):
        generation_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentInspectionResponse | ErrorResponse]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        document_id=document_id,
        generation_id=generation_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: UUID,
    document_id: UUID,
    *,
    client: AuthenticatedClient,
    generation_id: None | Unset | UUID = UNSET,
) -> DocumentInspectionResponse | ErrorResponse | None:
    """Inspect Document

    Args:
        project_id (UUID):
        document_id (UUID):
        generation_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentInspectionResponse | ErrorResponse
    """

    return sync_detailed(
        project_id=project_id,
        document_id=document_id,
        client=client,
        generation_id=generation_id,
    ).parsed


async def asyncio_detailed(
    project_id: UUID,
    document_id: UUID,
    *,
    client: AuthenticatedClient,
    generation_id: None | Unset | UUID = UNSET,
) -> Response[DocumentInspectionResponse | ErrorResponse]:
    """Inspect Document

    Args:
        project_id (UUID):
        document_id (UUID):
        generation_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentInspectionResponse | ErrorResponse]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        document_id=document_id,
        generation_id=generation_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: UUID,
    document_id: UUID,
    *,
    client: AuthenticatedClient,
    generation_id: None | Unset | UUID = UNSET,
) -> DocumentInspectionResponse | ErrorResponse | None:
    """Inspect Document

    Args:
        project_id (UUID):
        document_id (UUID):
        generation_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentInspectionResponse | ErrorResponse
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            document_id=document_id,
            client=client,
            generation_id=generation_id,
        )
    ).parsed
