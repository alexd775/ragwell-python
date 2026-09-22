"""Handwritten validation at the public search response boundary."""

from __future__ import annotations

from ._generated.models import RerankMetadata, SearchResponse
from ._generated.types import Unset
from .errors import ProtocolError

_SEARCH_OPERATION_ID = "search_v1_projects__project_id__search_post"


def validate_search_response(response: SearchResponse) -> None:
    """Reject union fallbacks that violate the declared reranking response type."""
    if response.rerank is not None and not isinstance(
        response.rerank, (RerankMetadata, Unset)
    ):
        raise ProtocolError(
            "Response did not match the reviewed API schema",
            operation_id=_SEARCH_OPERATION_ID,
        )
