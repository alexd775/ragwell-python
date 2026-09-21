"""Monotonic budgets shared by nested operations, isolated per thread/task."""

from __future__ import annotations

import math
from collections.abc import Callable
from contextvars import ContextVar, Token
from types import TracebackType

from .errors import RagwellError, TransportTimeout


def finite_seconds(value: float, name: str, *, zero: bool = False) -> float:
    if not math.isfinite(value) or value < 0 or (value == 0 and not zero):
        qualifier = "non-negative" if zero else "positive"
        raise ValueError(f"{name} must be finite and {qualifier}")
    return value


class Deadline:
    def __init__(
        self,
        seconds: float,
        clock: Callable[[], float],
        *,
        operation_id: str,
        parent: Deadline | None = None,
        error: Callable[[], RagwellError] | None = None,
    ) -> None:
        self.clock = clock
        self.expires = clock() + seconds
        self.parent = parent
        self.operation_id = operation_id
        self.error = error
        self.request_id: str | None = None

    def remaining(self) -> float:
        try:
            inherited = self.parent.remaining() if self.parent is not None else math.inf
        except RagwellError as caught:
            if self.request_id is not None:
                caught.request_id = self.request_id
            raise
        remaining = self.expires - self.clock()
        if remaining <= 0:
            error = (
                self.error()
                if self.error is not None
                else TransportTimeout(
                    "The operation deadline elapsed", operation_id=self.operation_id
                )
            )
            error.request_id = self.request_id
            raise error from None
        return min(remaining, inherited)

    def check(self) -> None:
        self.remaining()


class DeadlineScope:
    def __init__(self, context: ContextVar[Deadline | None], budget: Deadline) -> None:
        self.context = context
        self.budget = budget
        self.token: Token[Deadline | None] | None = None

    def __enter__(self) -> Deadline:
        self.token = self.context.set(self.budget)
        return self.budget

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        assert self.token is not None
        self.context.reset(self.token)
