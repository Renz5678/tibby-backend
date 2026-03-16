"""
rate_limiter.py — Tibby Chatbot Rate Limiter
Sliding-window rate limiter keyed by user IP address.
"""

from datetime import datetime, timedelta
from typing import Dict, List

from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW


class RateLimiter:
    """Sliding-window rate limiter for per-user request throttling."""

    def __init__(
        self,
        max_requests: int = RATE_LIMIT_REQUESTS,
        window: int = RATE_LIMIT_WINDOW,
    ):
        self.requests: Dict[str, List[datetime]] = {}
        self.max_requests = max_requests
        self.window = window

    def is_allowed(self, user_id: str) -> bool:
        """
        Return True if the user is within the rate limit.
        Automatically purges timestamps that fall outside the sliding window.
        """
        now = datetime.now()

        if user_id not in self.requests:
            self.requests[user_id] = []

        # Drop timestamps outside the current window
        self.requests[user_id] = [
            t for t in self.requests[user_id]
            if now - t < timedelta(seconds=self.window)
        ]

        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True

        return False


# Module-level singleton used across the app
rate_limiter = RateLimiter()
