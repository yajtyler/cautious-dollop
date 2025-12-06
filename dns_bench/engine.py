from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Sequence

from .exceptions import DNSBenchError, ProviderQueryError, ProviderRateLimitError
from .providers import DNSProvider


@dataclass(slots=True)
class QueryMeasurement:
    provider: str
    domain: str
    iteration: int
    attempts: int
    retry_count: int
    success: bool
    started_at: str
    finished_at: str
    latency_ms: float | None
    error_type: str | None
    error_message: str | None
    addresses: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "domain": self.domain,
            "iteration": self.iteration,
            "attempts": self.attempts,
            "retry_count": self.retry_count,
            "success": self.success,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "latency_ms": self.latency_ms,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "addresses": list(self.addresses),
        }


class BenchmarkEngine:
    """Core benchmarking engine that coordinates DNS queries."""

    def __init__(
        self,
        providers: Sequence[DNSProvider],
        domains: Sequence[str],
        iterations: int,
        *,
        concurrency: int,
        query_timeout: float,
        max_retries: int,
        backoff_base: float,
        backoff_max: float,
        backoff_jitter: float,
        rng: random.Random | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        if not providers:
            raise ValueError("At least one provider is required")
        if not domains:
            raise ValueError("At least one domain is required")

        self.providers = list(providers)
        self.domains = list(domains)
        self.iterations = iterations
        self.concurrency = max(1, concurrency)
        self.query_timeout = query_timeout
        self.max_retries = max(0, max_retries)
        self.backoff_base = max(0.0, backoff_base)
        self.backoff_max = max(self.backoff_base, backoff_max)
        self.backoff_jitter = max(0.0, backoff_jitter)
        self._rng = rng or random.Random()
        self.logger = logger or logging.getLogger("dns_bench")
        self.measurements: list[QueryMeasurement] = []
        self._semaphore = asyncio.Semaphore(self.concurrency)

    async def run(self) -> List[QueryMeasurement]:
        jobs = self._build_jobs()
        tasks = [asyncio.create_task(self._run_job(job)) for job in jobs]
        measurements: list[QueryMeasurement] = []
        for coro in asyncio.as_completed(tasks):
            result = await coro
            measurements.append(result)
            self.logger.info(
                "dns_bench.measurement %s",
                json.dumps(result.to_dict(), sort_keys=True),
            )
        self.measurements = measurements
        return measurements

    def _build_jobs(self) -> list[tuple[int, DNSProvider, str]]:
        jobs: list[tuple[int, DNSProvider, str]] = []
        for iteration in range(1, self.iterations + 1):
            providers = self.providers[:]
            domains = self.domains[:]
            self._rng.shuffle(providers)
            self._rng.shuffle(domains)
            for provider in providers:
                for domain in domains:
                    jobs.append((iteration, provider, domain))
        return jobs

    async def _run_job(self, job: tuple[int, DNSProvider, str]) -> QueryMeasurement:
        iteration, provider, domain = job
        async with self._semaphore:
            return await self._execute_with_retries(iteration, provider, domain)

    async def _execute_with_retries(
        self, iteration: int, provider: DNSProvider, domain: str
    ) -> QueryMeasurement:
        attempts = 0
        retries = 0
        addresses: list[str] = []
        while True:
            attempts += 1
            start = time.perf_counter()
            started_at = datetime.now(timezone.utc)
            latency_ms: float | None = None
            error_type: str | None = None
            error_message: str | None = None
            success = False
            try:
                async with asyncio.timeout(self.query_timeout):
                    addresses = list(await provider.query(domain, timeout=self.query_timeout))
                latency_ms = (time.perf_counter() - start) * 1000
                success = True
                finished_at = datetime.now(timezone.utc)
                return QueryMeasurement(
                    provider=provider.name,
                    domain=domain,
                    iteration=iteration,
                    attempts=attempts,
                    retry_count=retries,
                    success=success,
                    started_at=started_at.isoformat(),
                    finished_at=finished_at.isoformat(),
                    latency_ms=latency_ms,
                    error_type=error_type,
                    error_message=error_message,
                    addresses=addresses,
                )
            except ProviderRateLimitError as exc:  # exponential backoff and retry
                latency_ms = (time.perf_counter() - start) * 1000
                error_type = "rate_limit"
                error_message = str(exc)
                if retries >= self.max_retries:
                    finished_at = datetime.now(timezone.utc)
                    return QueryMeasurement(
                        provider=provider.name,
                        domain=domain,
                        iteration=iteration,
                        attempts=attempts,
                        retry_count=retries,
                        success=False,
                        started_at=started_at.isoformat(),
                        finished_at=finished_at.isoformat(),
                        latency_ms=latency_ms,
                        error_type=error_type,
                        error_message=error_message,
                        addresses=addresses,
                    )
                await asyncio.sleep(self._compute_backoff(retries))
                retries += 1
            except asyncio.TimeoutError:
                latency_ms = (time.perf_counter() - start) * 1000
                error_type = "timeout"
                error_message = f"Timed out querying {domain} via {provider.name}"
                finished_at = datetime.now(timezone.utc)
                return QueryMeasurement(
                    provider=provider.name,
                    domain=domain,
                    iteration=iteration,
                    attempts=attempts,
                    retry_count=retries,
                    success=False,
                    started_at=started_at.isoformat(),
                    finished_at=finished_at.isoformat(),
                    latency_ms=latency_ms,
                    error_type=error_type,
                    error_message=error_message,
                    addresses=addresses,
                )
            except (ProviderQueryError, DNSBenchError) as exc:
                latency_ms = (time.perf_counter() - start) * 1000
                error_type = exc.__class__.__name__
                error_message = str(exc)
                if retries >= self.max_retries:
                    finished_at = datetime.now(timezone.utc)
                    return QueryMeasurement(
                        provider=provider.name,
                        domain=domain,
                        iteration=iteration,
                        attempts=attempts,
                        retry_count=retries,
                        success=False,
                        started_at=started_at.isoformat(),
                        finished_at=finished_at.isoformat(),
                        latency_ms=latency_ms,
                        error_type=error_type,
                        error_message=error_message,
                        addresses=addresses,
                    )
                await asyncio.sleep(self._compute_backoff(retries))
                retries += 1
            except Exception as exc:  # pragma: no cover - defensive
                latency_ms = (time.perf_counter() - start) * 1000
                error_type = exc.__class__.__name__
                error_message = str(exc)
                finished_at = datetime.now(timezone.utc)
                return QueryMeasurement(
                    provider=provider.name,
                    domain=domain,
                    iteration=iteration,
                    attempts=attempts,
                    retry_count=retries,
                    success=False,
                    started_at=started_at.isoformat(),
                    finished_at=finished_at.isoformat(),
                    latency_ms=latency_ms,
                    error_type=error_type,
                    error_message=error_message,
                    addresses=addresses,
                )

    def _compute_backoff(self, retries: int) -> float:
        exponential = self.backoff_base * (2**retries)
        sleep_for = min(self.backoff_max, exponential)
        if self.backoff_jitter:
            sleep_for += self._rng.uniform(0, self.backoff_jitter)
        return sleep_for
