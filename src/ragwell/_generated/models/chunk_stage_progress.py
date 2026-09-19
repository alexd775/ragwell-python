from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.chunk_stage_progress_phase import ChunkStageProgressPhase

T = TypeVar("T", bound="ChunkStageProgress")


@_attrs_define
class ChunkStageProgress:
    completed_batches: int
    phase: ChunkStageProgressPhase
    total_batches: int

    def to_dict(self) -> dict[str, Any]:
        completed_batches = self.completed_batches

        phase = self.phase.value

        total_batches = self.total_batches

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "completed_batches": completed_batches,
                "phase": phase,
                "total_batches": total_batches,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        completed_batches = d.pop("completed_batches")

        phase = ChunkStageProgressPhase(d.pop("phase"))

        total_batches = d.pop("total_batches")

        chunk_stage_progress = cls(
            completed_batches=completed_batches,
            phase=phase,
            total_batches=total_batches,
        )

        return chunk_stage_progress
