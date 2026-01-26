import time

from src.app.core.exceptions.execution_exc import ExecutionRateLimited


class ExecutionRateLimiter:
    def __init__(self, max_requests: int, window_sec: int) -> None:
        """
        Initialize execution rate limiter.

        :param max_requests: max requests per window
        :param window_sec: window duration in seconds

        :return: None
        """
        self.max_requests = max_requests
        self.window_sec = window_sec
        self._buckets: dict[str, list[float]] = {}

    def check(self, key: str) -> None:
        """
        Enforce rate limit for the given key.

        :param key: rate limit key

        :return: None
        """
        now = time.time()
        window_start = now - self.window_sec
        bucket = self._buckets.get(key) or []
        bucket = [timestamp for timestamp in bucket if timestamp >= window_start]
        if len(bucket) >= self.max_requests:
            raise ExecutionRateLimited
        bucket.append(now)
        self._buckets[key] = bucket
