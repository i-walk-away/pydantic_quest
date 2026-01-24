from fastapi import Depends, Request

from src.app.core.dependencies.services.execution_rate_limiter import (
    get_execution_rate_limiter,
)
from src.app.domain.services.execution_rate_limiter import ExecutionRateLimiter


def enforce_execution_rate_limit(
        request: Request,
        rate_limiter: ExecutionRateLimiter = Depends(get_execution_rate_limiter),
) -> None:
    """
    Enforce code execution rate limit.

    :param request: request context
    :param rate_limiter: execution rate limiter

    :return: None
    """
    client = request.client
    key = client.host if client else "unknown"
    rate_limiter.check(key=key)
