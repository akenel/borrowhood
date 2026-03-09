"""Zero-dependency rate limiting middleware for FastAPI.

Uses in-memory dict + timestamps. No Redis, no slowapi, no Caddy plugin.
Limits per IP: reads (GET) get generous limits, writes (POST/PUT/PATCH/DELETE) are tighter.
"""

import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# Paths that skip rate limiting entirely
EXEMPT_PATHS = {"/health", "/api/docs", "/api/redoc", "/openapi.json", "/static"}


def _is_exempt(path: str) -> bool:
    for prefix in EXEMPT_PATHS:
        if path.startswith(prefix):
            return True
    return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP sliding window rate limiter.

    Args:
        app: ASGI app
        read_limit: max GET requests per window (default 120)
        write_limit: max POST/PUT/PATCH/DELETE requests per window (default 20)
        window_seconds: sliding window size in seconds (default 60)
        cleanup_interval: seconds between stale entry cleanup (default 300)
    """

    def __init__(
        self,
        app,
        read_limit: int = 120,
        write_limit: int = 20,
        window_seconds: int = 60,
        cleanup_interval: int = 300,
    ):
        super().__init__(app)
        self.read_limit = read_limit
        self.write_limit = write_limit
        self.window = window_seconds
        self.cleanup_interval = cleanup_interval
        # {ip: [(timestamp, is_write), ...]}
        self.requests: dict[str, list[tuple[float, bool]]] = defaultdict(list)
        self.last_cleanup = time.monotonic()

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _cleanup_stale(self, now: float):
        """Remove entries older than the window from all IPs."""
        if now - self.last_cleanup < self.cleanup_interval:
            return
        self.last_cleanup = now
        cutoff = now - self.window
        stale_ips = []
        for ip, entries in self.requests.items():
            self.requests[ip] = [(t, w) for t, w in entries if t > cutoff]
            if not self.requests[ip]:
                stale_ips.append(ip)
        for ip in stale_ips:
            del self.requests[ip]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if _is_exempt(path):
            return await call_next(request)

        now = time.monotonic()
        self._cleanup_stale(now)

        ip = self._get_client_ip(request)
        is_write = request.method in ("POST", "PUT", "PATCH", "DELETE")

        # Trim this IP's entries to current window
        cutoff = now - self.window
        entries = [(t, w) for t, w in self.requests[ip] if t > cutoff]

        # Count reads and writes separately
        read_count = sum(1 for _, w in entries if not w)
        write_count = sum(1 for _, w in entries if w)

        limit = self.write_limit if is_write else self.read_limit
        current = write_count if is_write else read_count

        if current >= limit:
            # Calculate retry-after from oldest entry in window
            oldest = min((t for t, w in entries if w == is_write), default=now)
            retry_after = int(self.window - (now - oldest)) + 1
            logger.warning("Rate limit hit: ip=%s method=%s path=%s count=%d/%d",
                           ip, request.method, path, current, limit)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
                headers={"Retry-After": str(retry_after)},
            )

        # Record this request
        entries.append((now, is_write))
        self.requests[ip] = entries

        return await call_next(request)
