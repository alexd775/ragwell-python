from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.attempt_status import AttemptStatus
from ..models.ingestion_stage import IngestionStage

T = TypeVar("T", bound="DocumentStageAttempt")


@_attrs_define
class DocumentStageAttempt:
    attempt_number: int
    error_code: None | str
    finished_at: datetime.datetime | None
    id: UUID
    job_id: UUID
    stage: IngestionStage
    started_at: datetime.datetime
    status: AttemptStatus
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attempt_number = self.attempt_number

        error_code: None | str
        error_code = self.error_code

        finished_at: None | str
        if isinstance(self.finished_at, datetime.datetime):
            finished_at = self.finished_at.isoformat()
        else:
            finished_at = self.finished_at

        id = str(self.id)

        job_id = str(self.job_id)

        stage = self.stage.value

        started_at = self.started_at.isoformat()

        status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attempt_number": attempt_number,
                "error_code": error_code,
                "finished_at": finished_at,
                "id": id,
                "job_id": job_id,
                "stage": stage,
                "started_at": started_at,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        attempt_number = d.pop("attempt_number")

        def _parse_error_code(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        error_code = _parse_error_code(d.pop("error_code"))

        def _parse_finished_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                finished_at_type_0 = datetime.datetime.fromisoformat(data)

                return finished_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        finished_at = _parse_finished_at(d.pop("finished_at"))

        id = UUID(d.pop("id"))

        job_id = UUID(d.pop("job_id"))

        stage = IngestionStage(d.pop("stage"))

        started_at = datetime.datetime.fromisoformat(d.pop("started_at"))

        status = AttemptStatus(d.pop("status"))

        document_stage_attempt = cls(
            attempt_number=attempt_number,
            error_code=error_code,
            finished_at=finished_at,
            id=id,
            job_id=job_id,
            stage=stage,
            started_at=started_at,
            status=status,
        )

        document_stage_attempt.additional_properties = d
        return document_stage_attempt

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
