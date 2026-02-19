"""Tests for benchmarking engine."""

from unittest.mock import MagicMock, patch

import dns.exception
import dns.resolver

from dns_bench.benchmark import BenchmarkResult, BenchmarkRunner, run_benchmark


class TestBenchmarkResult:
    """Test BenchmarkResult dataclass."""

    def test_benchmark_result_creation(self):
        """Test creating a benchmark result."""
        result = BenchmarkResult(
            provider="8.8.8.8",
            domain="google.com",
            latency_ms=45.5,
            success=True,
            error=None,
        )
        assert result.provider == "8.8.8.8"
        assert result.domain == "google.com"
        assert result.latency_ms == 45.5
        assert result.success is True
        assert result.error is None

    def test_benchmark_result_with_error(self):
        """Test creating a benchmark result with error."""
        result = BenchmarkResult(
            provider="1.1.1.1",
            domain="invalid.test",
            latency_ms=0.0,
            success=False,
            error="Timeout: Query exceeded time limit",
        )
        assert result.provider == "1.1.1.1"
        assert result.domain == "invalid.test"
        assert result.latency_ms == 0.0
        assert result.success is False
        assert result.error == "Timeout: Query exceeded time limit"


class TestBenchmarkRunner:
    """Test BenchmarkRunner class."""

    def test_benchmark_runner_initialization(self):
        """Test initializing a benchmark runner."""
        providers = ["8.8.8.8", "1.1.1.1"]
        domains = ["google.com", "github.com"]

        runner = BenchmarkRunner(
            providers=providers,
            domains=domains,
            timeout=5.0,
            iterations=2,
        )

        assert runner.providers == providers
        assert runner.domains == domains
        assert runner.timeout == 5.0
        assert runner.iterations == 2

    def test_benchmark_runner_default_timeout(self):
        """Test default timeout value."""
        runner = BenchmarkRunner(
            providers=["8.8.8.8"],
            domains=["google.com"],
        )
        assert runner.timeout == 5.0

    def test_benchmark_runner_default_iterations(self):
        """Test default iterations value."""
        runner = BenchmarkRunner(
            providers=["8.8.8.8"],
            domains=["google.com"],
        )
        assert runner.iterations == 1

    @patch("dns_bench.benchmark.dns.resolver.Resolver")
    def test_query_dns_success(self, mock_resolver_class):
        """Test successful DNS query."""
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver

        mock_answer = MagicMock()
        mock_answer.rrset = [MagicMock()]
        mock_resolver.resolve.return_value = mock_answer

        runner = BenchmarkRunner(
            providers=["8.8.8.8"],
            domains=["google.com"],
        )

        latency, success, error = runner._query_dns("8.8.8.8", "google.com")

        assert success is True
        assert error is None
        assert latency >= 0.0

    @patch("dns_bench.benchmark.dns.resolver.Resolver")
    def test_query_dns_timeout(self, mock_resolver_class):
        """Test DNS query timeout handling."""
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver
        mock_resolver.resolve.side_effect = dns.exception.Timeout()

        runner = BenchmarkRunner(
            providers=["8.8.8.8"],
            domains=["google.com"],
        )

        latency, success, error = runner._query_dns("8.8.8.8", "google.com")

        assert success is False
        assert "Timeout" in error
        assert latency >= 0.0

    @patch("dns_bench.benchmark.dns.resolver.Resolver")
    def test_query_dns_nxdomain(self, mock_resolver_class):
        """Test DNS query with non-existent domain."""
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver
        mock_resolver.resolve.side_effect = dns.resolver.NXDOMAIN()

        runner = BenchmarkRunner(
            providers=["8.8.8.8"],
            domains=["invalid.test"],
        )

        latency, success, error = runner._query_dns("8.8.8.8", "invalid.test")

        assert success is False
        assert "NXDOMAIN" in error
        assert latency >= 0.0

    @patch("dns_bench.benchmark.dns.resolver.Resolver")
    def test_query_dns_no_answer(self, mock_resolver_class):
        """Test DNS query with no answer."""
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver
        mock_resolver.resolve.side_effect = dns.resolver.NoAnswer()

        runner = BenchmarkRunner(
            providers=["8.8.8.8"],
            domains=["google.com"],
        )

        latency, success, error = runner._query_dns("8.8.8.8", "google.com")

        assert success is False
        assert "NoAnswer" in error
        assert latency >= 0.0

    @patch("dns_bench.benchmark.dns.resolver.Resolver")
    def test_query_dns_no_nameservers(self, mock_resolver_class):
        """Test DNS query with no nameservers."""
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver
        mock_resolver.resolve.side_effect = dns.resolver.NoNameservers()

        runner = BenchmarkRunner(
            providers=["8.8.8.8"],
            domains=["google.com"],
        )

        latency, success, error = runner._query_dns("8.8.8.8", "google.com")

        assert success is False
        assert "NoNameservers" in error
        assert latency >= 0.0

    @patch("dns_bench.benchmark.dns.resolver.Resolver")
    def test_query_dns_generic_exception(self, mock_resolver_class):
        """Test DNS query with generic exception."""
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver
        mock_resolver.resolve.side_effect = Exception("Test error")

        runner = BenchmarkRunner(
            providers=["8.8.8.8"],
            domains=["google.com"],
        )

        latency, success, error = runner._query_dns("8.8.8.8", "google.com")

        assert success is False
        assert "Test error" in error
        assert latency >= 0.0

    @patch("dns_bench.benchmark.dns.resolver.Resolver")
    def test_run_single_provider_domain(self, mock_resolver_class):
        """Test running benchmark with single provider and domain."""
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver

        mock_answer = MagicMock()
        mock_answer.rrset = [MagicMock()]
        mock_resolver.resolve.return_value = mock_answer

        runner = BenchmarkRunner(
            providers=["8.8.8.8"],
            domains=["google.com"],
            iterations=1,
        )

        results = runner.run()

        assert len(results) == 1
        assert results[0].provider == "8.8.8.8"
        assert results[0].domain == "google.com"
        assert results[0].success is True
        assert results[0].error is None

    @patch("dns_bench.benchmark.dns.resolver.Resolver")
    def test_run_multiple_providers(self, mock_resolver_class):
        """Test running benchmark with multiple providers."""
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver

        mock_answer = MagicMock()
        mock_answer.rrset = [MagicMock()]
        mock_resolver.resolve.return_value = mock_answer

        runner = BenchmarkRunner(
            providers=["8.8.8.8", "1.1.1.1"],
            domains=["google.com"],
            iterations=1,
        )

        results = runner.run()

        assert len(results) == 2
        providers_in_results = {r.provider for r in results}
        assert "8.8.8.8" in providers_in_results
        assert "1.1.1.1" in providers_in_results

    @patch("dns_bench.benchmark.dns.resolver.Resolver")
    def test_run_multiple_domains(self, mock_resolver_class):
        """Test running benchmark with multiple domains."""
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver

        mock_answer = MagicMock()
        mock_answer.rrset = [MagicMock()]
        mock_resolver.resolve.return_value = mock_answer

        runner = BenchmarkRunner(
            providers=["8.8.8.8"],
            domains=["google.com", "github.com"],
            iterations=1,
        )

        results = runner.run()

        assert len(results) == 2
        domains_in_results = {r.domain for r in results}
        assert "google.com" in domains_in_results
        assert "github.com" in domains_in_results

    @patch("dns_bench.benchmark.dns.resolver.Resolver")
    def test_run_multiple_iterations(self, mock_resolver_class):
        """Test running benchmark with multiple iterations."""
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver

        mock_answer = MagicMock()
        mock_answer.rrset = [MagicMock()]
        mock_resolver.resolve.return_value = mock_answer

        runner = BenchmarkRunner(
            providers=["8.8.8.8"],
            domains=["google.com"],
            iterations=3,
        )

        results = runner.run()

        assert len(results) == 3
        for result in results:
            assert result.provider == "8.8.8.8"
            assert result.domain == "google.com"

    @patch("dns_bench.benchmark.dns.resolver.Resolver")
    def test_run_complex_scenario(self, mock_resolver_class):
        """Test running benchmark with multiple providers, domains, and iterations."""
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver

        mock_answer = MagicMock()
        mock_answer.rrset = [MagicMock()]
        mock_resolver.resolve.return_value = mock_answer

        runner = BenchmarkRunner(
            providers=["8.8.8.8", "1.1.1.1"],
            domains=["google.com", "github.com"],
            iterations=2,
        )

        results = runner.run()

        expected_count = 2 * 2 * 2
        assert len(results) == expected_count

        for result in results:
            assert result.provider in ["8.8.8.8", "1.1.1.1"]
            assert result.domain in ["google.com", "github.com"]
            assert isinstance(result.latency_ms, float)
            assert isinstance(result.success, bool)

    @patch("dns_bench.benchmark.dns.resolver.Resolver")
    def test_run_mixed_success_failure(self, mock_resolver_class):
        """Test running benchmark with mixed success and failure."""
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver

        mock_answer = MagicMock()
        mock_answer.rrset = [MagicMock()]

        side_effects = [
            mock_answer,
            dns.exception.Timeout(),
            mock_answer,
        ]
        mock_resolver.resolve.side_effect = side_effects

        runner = BenchmarkRunner(
            providers=["8.8.8.8", "1.1.1.1"],
            domains=["google.com"],
            iterations=1,
        )

        results = runner.run()

        success_count = sum(1 for r in results if r.success)
        failure_count = sum(1 for r in results if not r.success)

        assert success_count >= 1
        assert failure_count >= 1


class TestRunBenchmarkFunction:
    """Test run_benchmark convenience function."""

    @patch("dns_bench.benchmark.BenchmarkRunner.run")
    def test_run_benchmark_function(self, mock_run):
        """Test run_benchmark convenience function."""
        expected_results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=45.0,
                success=True,
                error=None,
            )
        ]
        mock_run.return_value = expected_results

        results = run_benchmark(
            providers=["8.8.8.8"],
            domains=["google.com"],
            timeout=5.0,
            iterations=1,
        )

        assert results == expected_results

    @patch("dns_bench.benchmark.BenchmarkRunner.run")
    def test_run_benchmark_with_custom_timeout(self, mock_run):
        """Test run_benchmark with custom timeout."""
        mock_run.return_value = []

        run_benchmark(
            providers=["8.8.8.8"],
            domains=["google.com"],
            timeout=10.0,
            iterations=2,
        )

        mock_run.assert_called_once()

    @patch("dns_bench.benchmark.BenchmarkRunner")
    def test_run_benchmark_passes_parameters(self, mock_runner_class):
        """Test that run_benchmark passes parameters correctly."""
        mock_runner = MagicMock()
        mock_runner_class.return_value = mock_runner
        mock_runner.run.return_value = []

        run_benchmark(
            providers=["8.8.8.8", "1.1.1.1"],
            domains=["google.com", "github.com"],
            timeout=3.0,
            iterations=5,
        )

        mock_runner_class.assert_called_once_with(
            providers=["8.8.8.8", "1.1.1.1"],
            domains=["google.com", "github.com"],
            timeout=3.0,
            iterations=5,
        )
        mock_runner.run.assert_called_once()
