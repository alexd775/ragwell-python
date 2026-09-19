"""Stable, redacted SDK exceptions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ._generated.models import FieldError, PlanLimitErrorDetail


class RagwellError(Exception):
    """Base class for all SDK-originated failures."""


class ConfigurationError(RagwellError, ValueError):
    """The client configuration is missing or unsafe."""


class ProtocolError(RagwellError):
    """The peer returned a response that does not match the reviewed contract."""

    def __init__(self, message: str, *, operation_id: str | None = None) -> None:
        super().__init__(message)
        self.operation_id = operation_id
        self.identifiers: dict[str, str] = {}

    def with_identifiers(self, **identifiers: object) -> ProtocolError:
        self.identifiers.update(
            {
                name: str(value)
                for name, value in identifiers.items()
                if value is not None
            }
        )
        return self


class TransportError(RagwellError):
    """A request could not be completed at the HTTP transport boundary."""

    def __init__(self, message: str, *, operation_id: str | None = None) -> None:
        super().__init__(message)
        self.operation_id = operation_id
        self.identifiers: dict[str, str] = {}

    def with_identifiers(self, **identifiers: object) -> TransportError:
        self.identifiers.update(
            {
                name: str(value)
                for name, value in identifiers.items()
                if value is not None
            }
        )
        return self


class TransportTimeout(TransportError):
    """The finite operation deadline or an HTTP timeout elapsed."""


class ApiError(RagwellError):
    """A typed, bounded API status failure."""

    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        operation_id: str,
        request_id: str | None = None,
        field_errors: Sequence[FieldError] = (),
        retry_after: float | None = None,
        quota: PlanLimitErrorDetail | None = None,
        identifiers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(f"{code}: {message}")
        self.status_code = status_code
        self.code = code
        self.safe_message = message
        self.operation_id = operation_id
        self.request_id = request_id
        self.field_errors = tuple(field_errors)
        self.retry_after = retry_after
        self.quota = quota
        self.identifiers = dict(identifiers or {})

    def with_identifiers(self, **identifiers: object) -> ApiError:
        """Attach already-known resource identifiers without changing the error."""
        self.identifiers.update(
            {
                name: str(value)
                for name, value in identifiers.items()
                if value is not None
            }
        )
        return self

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(status_code={self.status_code!r}, "
            f"code={self.code!r}, operation_id={self.operation_id!r}, "
            f"request_id={self.request_id!r})"
        )


class AuthenticationError(ApiError):
    """The API key is missing, expired, revoked, or otherwise invalid."""


class PermissionDeniedError(ApiError):
    """The principal lacks the required scope or current resource grant."""


class NotFoundError(ApiError):
    """The resource is absent or deliberately undisclosed."""


class ConflictError(ApiError):
    """The command conflicts with current resource or idempotency state."""


class ValidationError(ApiError):
    """The request failed bounded server validation."""


class RateLimitError(ApiError):
    """Temporary admission or rate limiting prevented the operation."""


class QuotaExceededError(ApiError):
    """A fixed plan quota prevented the operation and should not be retried."""


class ServerError(ApiError):
    """The application or an upstream dependency failed."""


class WaitTimeoutError(RagwellError):
    """Local observation stopped at its deadline; remote work was not cancelled."""

    def __init__(
        self,
        resource: str,
        *,
        identifiers: Mapping[str, object],
        timeout: float,
    ) -> None:
        super().__init__(
            f"Timed out waiting {timeout:g}s for {resource}; remote work may continue"
        )
        self.resource = resource
        self.identifiers = {name: str(value) for name, value in identifiers.items()}
        self.timeout = timeout


class OperationFailedError(RagwellError):
    """A waiter observed a terminal non-success resource state."""

    def __init__(
        self,
        resource: str,
        state: str,
        *,
        identifiers: Mapping[str, object],
        error_code: str | None = None,
        resource_value: Any = None,
    ) -> None:
        detail = f" ({error_code})" if error_code else ""
        super().__init__(f"{resource} reached terminal state {state}{detail}")
        self.resource = resource
        self.state = state
        self.error_code = error_code
        self.identifiers = {name: str(value) for name, value in identifiers.items()}
        self.resource_value = resource_value


class PaginationError(ProtocolError):
    """Pagination returned a repeated or otherwise unsafe continuation cursor."""


@dataclass(frozen=True, slots=True)
class IntegrityMismatch:
    expected_size: int
    actual_size: int
    expected_sha256: str
    actual_sha256: str


class DownloadIntegrityError(RagwellError):
    """A downloaded export part did not match its manifest."""

    def __init__(self, mismatch: IntegrityMismatch) -> None:
        super().__init__("Downloaded export part failed size or SHA-256 verification")
        self.mismatch = mismatch


__all__ = [
    "ApiError",
    "AuthenticationError",
    "ConfigurationError",
    "ConflictError",
    "DownloadIntegrityError",
    "IntegrityMismatch",
    "NotFoundError",
    "OperationFailedError",
    "PaginationError",
    "PermissionDeniedError",
    "ProtocolError",
    "QuotaExceededError",
    "RagwellError",
    "RateLimitError",
    "ServerError",
    "TransportError",
    "TransportTimeout",
    "ValidationError",
    "WaitTimeoutError",
]
