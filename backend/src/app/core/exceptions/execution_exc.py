from fastapi import HTTPException


class ExecutionRateLimited(HTTPException):
    """
    Execution rate limit exceeded.
    """
    status_code = 429
    detail = "Too many execution requests."

    def __init__(self) -> None:
        """
        Initialize execution rate limit error.

        :return: None
        """
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
        )


class ExecutionServiceUnavailable(HTTPException):
    """
    Execution service is unavailable.
    """
    status_code = 503
    detail = "Code execution service unavailable."

    def __init__(self) -> None:
        """
        Initialize execution service unavailable error.

        :return: None
        """
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
        )


class ExecutionInvalidOutput(HTTPException):
    """
    Execution output is invalid.
    """
    status_code = 500
    detail = "Execution output is invalid."

    def __init__(self) -> None:
        """
        Initialize execution output error.

        :return: None
        """
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
        )


class ExecutionPayloadTooLarge(HTTPException):
    """
    Execution payload is too large.
    """
    status_code = 413
    detail = "Execution payload is too large."

    def __init__(self) -> None:
        """
        Initialize execution payload too large error.

        :return: None
        """
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
        )
