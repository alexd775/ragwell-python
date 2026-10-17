from enum import StrEnum


class PlanLimitErrorDetailCode(StrEnum):
    PLAN_LIMIT_EMBEDDING_INPUT_TOKENS = "plan_limit_embedding_input_tokens"
    PLAN_LIMIT_EXCEEDED = "plan_limit_exceeded"

    def __str__(self) -> str:
        return str(self.value)
