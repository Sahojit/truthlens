"""
Simple in-memory token-bucket rate limiter middleware.
"""

import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self._store: dict = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Skip rate-limiting for health & docs endpoints
        if request.url.path in {"/health", "/docs", "/redoc", "/openapi.json", "/"}:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window

        # Prune old requests
        self._store[client_ip] = [
            t for t in self._store[client_ip] if t > window_start
        ]

        if len(self._store[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Max {self.max_requests} requests per {self.window}s."
                },
            )

        self._store[client_ip].append(now)
        return await call_next(request)
