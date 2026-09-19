"""Stable public data models generated from the reviewed machine contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ._generated.models import *  # noqa: F403
from ._generated.models import (
    DocumentExportPartResponse,
    FinalizedIntakeResponse,
    IngestionJobResponse,
)
from ._generated.models import __all__ as _GENERATED_ALL
from ._generated.types import UNSET, Unset


@dataclass(frozen=True, slots=True)
class UploadCompletion:
    """The accepted intake plus the later successfully observed job."""

    intake: FinalizedIntakeResponse
    job: IngestionJobResponse


@dataclass(frozen=True, slots=True)
class DownloadResult:
    """A verified export part saved atomically at ``path``."""

    path: Path
    part: DocumentExportPartResponse


__all__ = (*_GENERATED_ALL, "DownloadResult", "UNSET", "Unset", "UploadCompletion")
