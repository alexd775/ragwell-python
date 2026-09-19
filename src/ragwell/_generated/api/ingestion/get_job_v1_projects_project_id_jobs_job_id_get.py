from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.ingestion_job_response import IngestionJobResponse
from ...types import Response


def _get_kwargs(
    project_id: UUID,
    job_id: UUID,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/projects/{project_id}/jobs/{job_id}".format(
            project_id=quote(str(project_id), safe=""),
            job_id=quote(str(job_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ErrorResponse | IngestionJobResponse | None:
    if response.status_code == 200:
        response_200 = IngestionJobResponse.from_dict(response.json())

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
) -> Response[ErrorResponse | IngestionJobResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: UUID,
    job_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[ErrorResponse | IngestionJobResponse]:
    """Get Job

    Args:
        project_id (UUID):
        job_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | IngestionJobResponse]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        job_id=job_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: UUID,
    job_id: UUID,
    *,
    client: AuthenticatedClient,
) -> ErrorResponse | IngestionJobResponse | None:
    """Get Job

    Args:
        project_id (UUID):
        job_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | IngestionJobResponse
    """

    return sync_detailed(
        project_id=project_id,
        job_id=job_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    project_id: UUID,
    job_id: UUID,
    *,
    client: AuthenticatedClient,
) -> Response[ErrorResponse | IngestionJobResponse]:
    """Get Job

    Args:
        project_id (UUID):
        job_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | IngestionJobResponse]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        job_id=job_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: UUID,
    job_id: UUID,
    *,
    client: AuthenticatedClient,
) -> ErrorResponse | IngestionJobResponse | None:
    """Get Job

    Args:
        project_id (UUID):
        job_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | IngestionJobResponse
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            job_id=job_id,
            client=client,
        )
    ).parsed
