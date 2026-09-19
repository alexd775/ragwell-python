from http import HTTPStatus
from io import BytesIO
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...types import File, Response


def _get_kwargs(
    project_id: UUID,
    document_id: UUID,
    export_id: UUID,
    part_number: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/projects/{project_id}/documents/{document_id}/exports/{export_id}/parts/{part_number}".format(
            project_id=quote(str(project_id), safe=""),
            document_id=quote(str(document_id), safe=""),
            export_id=quote(str(export_id), safe=""),
            part_number=quote(str(part_number), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | File | None:
    if response.status_code == 200:
        response_200 = File(payload=BytesIO(response.content))

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
) -> Response[ErrorResponse | File]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: UUID,
    document_id: UUID,
    export_id: UUID,
    part_number: int,
    *,
    client: AuthenticatedClient,
) -> Response[ErrorResponse | File]:
    """Download Document Export Part

    Args:
        project_id (UUID):
        document_id (UUID):
        export_id (UUID):
        part_number (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | File]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        document_id=document_id,
        export_id=export_id,
        part_number=part_number,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: UUID,
    document_id: UUID,
    export_id: UUID,
    part_number: int,
    *,
    client: AuthenticatedClient,
) -> ErrorResponse | File | None:
    """Download Document Export Part

    Args:
        project_id (UUID):
        document_id (UUID):
        export_id (UUID):
        part_number (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | File
    """

    return sync_detailed(
        project_id=project_id,
        document_id=document_id,
        export_id=export_id,
        part_number=part_number,
        client=client,
    ).parsed


async def asyncio_detailed(
    project_id: UUID,
    document_id: UUID,
    export_id: UUID,
    part_number: int,
    *,
    client: AuthenticatedClient,
) -> Response[ErrorResponse | File]:
    """Download Document Export Part

    Args:
        project_id (UUID):
        document_id (UUID):
        export_id (UUID):
        part_number (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | File]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        document_id=document_id,
        export_id=export_id,
        part_number=part_number,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: UUID,
    document_id: UUID,
    export_id: UUID,
    part_number: int,
    *,
    client: AuthenticatedClient,
) -> ErrorResponse | File | None:
    """Download Document Export Part

    Args:
        project_id (UUID):
        document_id (UUID):
        export_id (UUID):
        part_number (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | File
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            document_id=document_id,
            export_id=export_id,
            part_number=part_number,
            client=client,
        )
    ).parsed
