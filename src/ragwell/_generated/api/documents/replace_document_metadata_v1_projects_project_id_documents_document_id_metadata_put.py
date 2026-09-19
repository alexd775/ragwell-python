from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_response import DocumentResponse
from ...models.error_response import ErrorResponse
from ...models.replace_document_metadata_request import ReplaceDocumentMetadataRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    project_id: UUID,
    document_id: UUID,
    *,
    body: ReplaceDocumentMetadataRequest,
    idempotency_key: None | str | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(idempotency_key, Unset):
        headers["Idempotency-Key"] = idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v1/projects/{project_id}/documents/{document_id}/metadata".format(
            project_id=quote(str(project_id), safe=""),
            document_id=quote(str(document_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DocumentResponse | ErrorResponse | None:
    if response.status_code == 200:
        response_200 = DocumentResponse.from_dict(response.json())

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
) -> Response[DocumentResponse | ErrorResponse]:
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
    body: ReplaceDocumentMetadataRequest,
    idempotency_key: None | str | Unset = UNSET,
) -> Response[DocumentResponse | ErrorResponse]:
    """Replace Document Metadata

    Args:
        project_id (UUID):
        document_id (UUID):
        idempotency_key (None | str | Unset): One key per logical command. Replay is guaranteed
            for 24 hours; omit only for single-attempt calls.
        body (ReplaceDocumentMetadataRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentResponse | ErrorResponse]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        document_id=document_id,
        body=body,
        idempotency_key=idempotency_key,
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
    body: ReplaceDocumentMetadataRequest,
    idempotency_key: None | str | Unset = UNSET,
) -> DocumentResponse | ErrorResponse | None:
    """Replace Document Metadata

    Args:
        project_id (UUID):
        document_id (UUID):
        idempotency_key (None | str | Unset): One key per logical command. Replay is guaranteed
            for 24 hours; omit only for single-attempt calls.
        body (ReplaceDocumentMetadataRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentResponse | ErrorResponse
    """

    return sync_detailed(
        project_id=project_id,
        document_id=document_id,
        client=client,
        body=body,
        idempotency_key=idempotency_key,
    ).parsed


async def asyncio_detailed(
    project_id: UUID,
    document_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ReplaceDocumentMetadataRequest,
    idempotency_key: None | str | Unset = UNSET,
) -> Response[DocumentResponse | ErrorResponse]:
    """Replace Document Metadata

    Args:
        project_id (UUID):
        document_id (UUID):
        idempotency_key (None | str | Unset): One key per logical command. Replay is guaranteed
            for 24 hours; omit only for single-attempt calls.
        body (ReplaceDocumentMetadataRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocumentResponse | ErrorResponse]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        document_id=document_id,
        body=body,
        idempotency_key=idempotency_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: UUID,
    document_id: UUID,
    *,
    client: AuthenticatedClient,
    body: ReplaceDocumentMetadataRequest,
    idempotency_key: None | str | Unset = UNSET,
) -> DocumentResponse | ErrorResponse | None:
    """Replace Document Metadata

    Args:
        project_id (UUID):
        document_id (UUID):
        idempotency_key (None | str | Unset): One key per logical command. Replay is guaranteed
            for 24 hours; omit only for single-attempt calls.
        body (ReplaceDocumentMetadataRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocumentResponse | ErrorResponse
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            document_id=document_id,
            client=client,
            body=body,
            idempotency_key=idempotency_key,
        )
    ).parsed
