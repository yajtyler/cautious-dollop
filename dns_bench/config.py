from __future__ import annotations

from typing import Final

DEFAULT_ITERATIONS: Final[int] = 3
DEFAULT_CONCURRENCY: Final[int] = 10
DEFAULT_TIMEOUT: Final[float] = 1.5
DEFAULT_MAX_RETRIES: Final[int] = 3
DEFAULT_BACKOFF_BASE: Final[float] = 0.2
DEFAULT_BACKOFF_MAX: Final[float] = 2.5
DEFAULT_BACKOFF_JITTER: Final[float] = 0.1
DEFAULT_DOMAINS: Final[list[str]] = [
    "example.com",
    "openai.com",
    "cloudflare.com",
    "python.org",
    "ietf.org",
]
DEFAULT_PROVIDER_KEYS: Final[list[str]] = [
    "system",
    "sim-stable",
    "sim-flaky",
]
