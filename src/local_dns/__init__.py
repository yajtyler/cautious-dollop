"""Local DNS resolver detection package."""

from .detector import (
    DetectionReport,
    DetectorConfig,
    ResolverEndpoint,
    detect_resolvers,
    parse_override_addresses,
)

__all__ = [
    "DetectionReport",
    "DetectorConfig",
    "ResolverEndpoint",
    "detect_resolvers",
    "parse_override_addresses",
]
