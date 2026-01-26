from src.app.domain.services.execution_rate_limiter import ExecutionRateLimiter
from src.cfg.cfg import settings

_rate_limiter = ExecutionRateLimiter(
    max_requests=settings.execution.rate_limit_max,
    window_sec=settings.execution.rate_limit_window_sec,
)


def get_execution_rate_limiter() -> ExecutionRateLimiter:
    """
    Build execution rate limiter.

    :return: execution rate limiter
    """
    return _rate_limiter
