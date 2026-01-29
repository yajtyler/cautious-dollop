"""DNS benchmarking engine for performance testing."""

import time
import concurrent.futures
from dataclasses import asdict, dataclass
from typing import List, Optional

import dns.rdatatype
import dns.resolver


@dataclass
class BenchmarkResult:
    """Single benchmark result for a DNS query."""

    provider: str
    domain: str
    latency_ms: float
    success: bool
    error: Optional[str] = None


class BenchmarkRunner:
    """
    Run DNS benchmarks against multiple providers and domains.

    Performs DNS A record lookups for each provider + domain combination,
    measuring latency and capturing success/failure information.
    """

    def __init__(
        self,
        providers: List[str],
        domains: List[str],
        timeout: float = 5.0,
        iterations: int = 1,
    ) -> None:
        """
        Initialize BenchmarkRunner.

        Args:
            providers: List of DNS provider IP addresses
            domains: List of domain names to query
            timeout: Query timeout in seconds (default: 5.0)
            iterations: Number of times to query each provider+domain (default: 1)
        """
        self.providers = providers
        self.domains = domains
        self.timeout = timeout
        self.iterations = iterations

    def _query_dns(self, provider_ip: str, domain: str) -> tuple[float, bool, Optional[str]]:
        """
        Perform a single DNS A record query.

        Args:
            provider_ip: DNS provider IP address
            domain: Domain name to query

        Returns:
            Tuple of (latency_ms, success, error_message)
            - latency_ms: Latency in milliseconds (0.0 if failed)
            - success: True if query succeeded, False otherwise
            - error_message: Error message if query failed, None if successful
        """
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [provider_ip]
        resolver.timeout = self.timeout
        resolver.lifetime = self.timeout

        start_time = time.time()
        try:
            resolver.resolve(domain, dns.rdatatype.A)
            latency_ms = (time.time() - start_time) * 1000
            return latency_ms, True, None
        except dns.resolver.NXDOMAIN:
            latency_ms = (time.time() - start_time) * 1000
            return latency_ms, False, "NXDOMAIN: Domain does not exist"
        except dns.resolver.NoAnswer:
            latency_ms = (time.time() - start_time) * 1000
            return latency_ms, False, "NoAnswer: No A record found"
        except dns.exception.Timeout:
            latency_ms = (time.time() - start_time) * 1000
            return latency_ms, False, "Timeout: Query exceeded time limit"
        except dns.resolver.NoNameservers:
            latency_ms = (time.time() - start_time) * 1000
            return latency_ms, False, "NoNameservers: Unable to reach nameserver"
        except dns.exception.DNSException as e:
            latency_ms = (time.time() - start_time) * 1000
            return latency_ms, False, f"DNSException: {str(e)}"
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return latency_ms, False, f"Error: {str(e)}"

    def run(self) -> List[dict]:
        """
        Run benchmarks for all provider + domain combinations.

        Returns:
            List of benchmark results as dictionaries with keys:
            - provider: DNS provider IP address
            - domain: Domain name queried
            - latency_ms: Query latency in milliseconds
            - success: True if query succeeded, False otherwise
            - error: Error message (None if successful)
        """
        results: List[BenchmarkResult] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_meta = {}
            for provider in self.providers:
                for domain in self.domains:
                    for _ in range(self.iterations):
                        future = executor.submit(self._query_dns, provider, domain)
                        future_to_meta[future] = (provider, domain)

            for future in concurrent.futures.as_completed(future_to_meta):
                provider, domain = future_to_meta[future]
                try:
                    latency_ms, success, error = future.result()
                    result = BenchmarkResult(
                        provider=provider,
                        domain=domain,
                        latency_ms=latency_ms,
                        success=success,
                        error=error,
                    )
                    results.append(result)
                except Exception as exc:
                    result = BenchmarkResult(
                        provider=provider,
                        domain=domain,
                        latency_ms=0.0,
                        success=False,
                        error=f"Unexpected error: {exc}",
                    )
                    results.append(result)

        return [asdict(result) for result in results]


def run_benchmark(
    providers: List[str],
    domains: List[str],
    timeout: float = 5.0,
    iterations: int = 1,
) -> List[dict]:
    """
    Convenience function to run benchmarks.

    Args:
        providers: List of DNS provider IP addresses
        domains: List of domain names to query
        timeout: Query timeout in seconds (default: 5.0)
        iterations: Number of times to query each provider+domain (default: 1)

    Returns:
        List of benchmark results as dictionaries
    """
    runner = BenchmarkRunner(
        providers=providers,
        domains=domains,
        timeout=timeout,
        iterations=iterations,
    )
    return runner.run()
