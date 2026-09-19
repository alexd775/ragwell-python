from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_upload_request import CreateUploadRequest
from ...models.error_response import ErrorResponse
from ...models.plan_limit_error_response import PlanLimitErrorResponse
from ...models.upload_session_response import UploadSessionResponse
from ...types import Response


def _get_kwargs(
    project_id: UUID,
    *,
    body: CreateUploadRequest,
    idempotency_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["Idempotency-Key"] = idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/projects/{project_id}/uploads".format(
            project_id=quote(str(project_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    ErrorResponse
    | ErrorResponse
    | PlanLimitErrorResponse
    | UploadSessionResponse
    | None
):
    if response.status_code == 201:
        response_201 = UploadSessionResponse.from_dict(response.json())

        return response_201

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

        def _parse_response_409(data: object) -> ErrorResponse | PlanLimitErrorResponse:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_409_type_0 = ErrorResponse.from_dict(data)

                return response_409_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            response_409_type_1 = PlanLimitErrorResponse.from_dict(data)

            return response_409_type_1

        response_409 = _parse_response_409(response.json())

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
) -> Response[
    ErrorResponse | ErrorResponse | PlanLimitErrorResponse | UploadSessionResponse
]:
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
    body: CreateUploadRequest,
    idempotency_key: str,
) -> Response[
    ErrorResponse | ErrorResponse | PlanLimitErrorResponse | UploadSessionResponse
]:
    """Create Upload

    Args:
        project_id (UUID):
        idempotency_key (str):
        body (CreateUploadRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | ErrorResponse | PlanLimitErrorResponse | UploadSessionResponse]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        body=body,
        idempotency_key=idempotency_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    project_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CreateUploadRequest,
    idempotency_key: str,
) -> (
    ErrorResponse
    | ErrorResponse
    | PlanLimitErrorResponse
    | UploadSessionResponse
    | None
):
    """Create Upload

    Args:
        project_id (UUID):
        idempotency_key (str):
        body (CreateUploadRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | ErrorResponse | PlanLimitErrorResponse | UploadSessionResponse
    """

    return sync_detailed(
        project_id=project_id,
        client=client,
        body=body,
        idempotency_key=idempotency_key,
    ).parsed


async def asyncio_detailed(
    project_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CreateUploadRequest,
    idempotency_key: str,
) -> Response[
    ErrorResponse | ErrorResponse | PlanLimitErrorResponse | UploadSessionResponse
]:
    """Create Upload

    Args:
        project_id (UUID):
        idempotency_key (str):
        body (CreateUploadRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ErrorResponse | ErrorResponse | PlanLimitErrorResponse | UploadSessionResponse]
    """

    kwargs = _get_kwargs(
        project_id=project_id,
        body=body,
        idempotency_key=idempotency_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    project_id: UUID,
    *,
    client: AuthenticatedClient,
    body: CreateUploadRequest,
    idempotency_key: str,
) -> (
    ErrorResponse
    | ErrorResponse
    | PlanLimitErrorResponse
    | UploadSessionResponse
    | None
):
    """Create Upload

    Args:
        project_id (UUID):
        idempotency_key (str):
        body (CreateUploadRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ErrorResponse | ErrorResponse | PlanLimitErrorResponse | UploadSessionResponse
    """

    return (
        await asyncio_detailed(
            project_id=project_id,
            client=client,
            body=body,
            idempotency_key=idempotency_key,
        )
    ).parsed
