"""Validate the bounded description projection before exposing it to agents."""

from uuid import UUID

from ._generated.models import ProjectAgentDescriptionResponse
from .errors import ProtocolError


def validate_agent_description(
    result: ProjectAgentDescriptionResponse, project_id: UUID
) -> None:
    if result.project_id != project_id or (
        result.description is not None
        and (not isinstance(result.description, str) or len(result.description) > 2000)
    ):
        raise ProtocolError(
            "Response did not match the requested project's description contract",
            operation_id="get_project_agent_description",
        )
