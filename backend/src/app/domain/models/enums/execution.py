from enum import StrEnum


class ExecutionStatus(StrEnum):
    """
    Execution status definition.
    """

    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    COMPILE_ERROR = "compile_error"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
