from __future__ import annotations


class DNSBenchError(Exception):
    """Base error for benchmark failures."""


class ProviderQueryError(DNSBenchError):
    """Raised when a DNS provider returns an error response."""


class ProviderRateLimitError(DNSBenchError):
    """Raised when a provider indicates rate limiting."""
