"""Typed synchronous and asynchronous clients for the Ragwell retrieval API."""

from ._version import __version__
from .async_client import AsyncRagwell
from .client import Ragwell
from .errors import (
    ApiError,
    AuthenticationError,
    ConfigurationError,
    ConflictError,
    DownloadIntegrityError,
    NotFoundError,
    OperationFailedError,
    PaginationError,
    PermissionDeniedError,
    ProtocolError,
    QuotaExceededError,
    RagwellError,
    RateLimitError,
    ServerError,
    TransportError,
    TransportTimeout,
    ValidationError,
    WaitTimeoutError,
)

__all__ = [
    "ApiError",
    "AsyncRagwell",
    "AuthenticationError",
    "ConfigurationError",
    "ConflictError",
    "DownloadIntegrityError",
    "NotFoundError",
    "OperationFailedError",
    "PaginationError",
    "PermissionDeniedError",
    "ProtocolError",
    "QuotaExceededError",
    "Ragwell",
    "RagwellError",
    "RateLimitError",
    "ServerError",
    "TransportError",
    "TransportTimeout",
    "ValidationError",
    "WaitTimeoutError",
    "__version__",
]
