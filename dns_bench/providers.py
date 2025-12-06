from __future__ import annotations

import asyncio
import random
import socket
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Protocol, Sequence

from .exceptions import ProviderQueryError, ProviderRateLimitError


class DNSProvider(Protocol):
    """Protocol describing a DNS provider implementation."""

    name: str

    async def query(self, domain: str, timeout: float | None = None) -> Sequence[str]:
        """Resolve *domain* and return a list of address strings."""


@dataclass(slots=True)
class SystemResolverProvider:
    """Provider that uses the host resolver via asyncio.getaddrinfo."""

    name: str = "system"

    async def query(self, domain: str, timeout: float | None = None) -> Sequence[str]:
        loop = asyncio.get_running_loop()
        infos = await loop.getaddrinfo(domain, None, proto=socket.IPPROTO_TCP)
        addresses: list[str] = []
        for info in infos:
            sockaddr = info[4]
            if sockaddr and sockaddr[0] not in addresses:
                addresses.append(sockaddr[0])
        return addresses


@dataclass(slots=True)
class SimulatedDNSProvider:
    """Provider that simulates DNS latency and failures for testing."""

    name: str
    min_latency: float = 0.02
    max_latency: float = 0.25
    failure_rate: float = 0.05
    timeout_rate: float = 0.05
    rate_limit_rate: float = 0.02
    rng: random.Random = field(default_factory=random.Random)

    async def query(self, domain: str, timeout: float | None = None) -> Sequence[str]:
        latency = self.rng.uniform(self.min_latency, self.max_latency)
        await asyncio.sleep(latency)

        roll = self.rng.random()
        if roll < self.rate_limit_rate:
            raise ProviderRateLimitError(f"{self.name} throttled request for {domain}")
        roll -= self.rate_limit_rate

        if roll < self.timeout_rate:
            # Sleep beyond timeout to trigger the outer timeout handler.
            delay = timeout * 2 if timeout else self.max_latency * 4
            await asyncio.sleep(delay)
            return []
        roll -= self.timeout_rate

        if roll < self.failure_rate:
            raise ProviderQueryError(f"{self.name} failed to resolve {domain}")

        return [f"198.51.100.{self.rng.randint(1, 254)}"]


def provider_catalog() -> Dict[str, Callable[[], DNSProvider]]:
    """Return the built-in provider factory mapping."""

    return {
        "system": SystemResolverProvider,
        "sim-stable": lambda: SimulatedDNSProvider(
            name="sim-stable",
            min_latency=0.015,
            max_latency=0.05,
            failure_rate=0.01,
            timeout_rate=0.01,
            rate_limit_rate=0.01,
        ),
        "sim-flaky": lambda: SimulatedDNSProvider(
            name="sim-flaky",
            min_latency=0.03,
            max_latency=0.3,
            failure_rate=0.15,
            timeout_rate=0.1,
            rate_limit_rate=0.08,
        ),
        "sim-slow": lambda: SimulatedDNSProvider(
            name="sim-slow",
            min_latency=0.1,
            max_latency=0.6,
            failure_rate=0.05,
            timeout_rate=0.05,
            rate_limit_rate=0.02,
        ),
    }


def build_providers(keys: Sequence[str] | None) -> List[DNSProvider]:
    factories = provider_catalog()
    selected = keys or list(factories.keys())
    providers: list[DNSProvider] = []
    for key in selected:
        factory = factories.get(key)
        if not factory:
            available = ", ".join(sorted(factories.keys()))
            raise ValueError(f"Unknown provider '{key}'. Available: {available}")
        providers.append(factory())
    return providers
