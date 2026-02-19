"""Tests for results analysis and display module."""

from io import StringIO

from rich.console import Console

from dns_bench.benchmark import BenchmarkResult
from dns_bench.results import ProviderMetrics, ResultsAnalyzer, display_results


class TestProviderMetrics:
    """Test ProviderMetrics dataclass."""

    def test_provider_metrics_creation(self):
        """Test creating provider metrics."""
        metrics = ProviderMetrics(
            provider="8.8.8.8",
            avg_latency=45.5,
            median_latency=44.0,
            success_rate=100.0,
            sample_count=10,
        )
        assert metrics.provider == "8.8.8.8"
        assert metrics.avg_latency == 45.5
        assert metrics.median_latency == 44.0
        assert metrics.success_rate == 100.0
        assert metrics.sample_count == 10


class TestResultsAnalyzer:
    """Test ResultsAnalyzer class."""

    def test_analyzer_initialization(self):
        """Test initializing analyzer with results."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=45.0,
                success=True,
                error=None,
            )
        ]
        analyzer = ResultsAnalyzer(results)
        assert analyzer.results == results

    def test_analyze_single_provider_single_result(self):
        """Test analyzing single result for one provider."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=45.0,
                success=True,
                error=None,
            )
        ]
        analyzer = ResultsAnalyzer(results)
        metrics = analyzer.analyze()

        assert len(metrics) == 1
        assert metrics[0].provider == "8.8.8.8"
        assert metrics[0].avg_latency == 45.0
        assert metrics[0].median_latency == 45.0
        assert metrics[0].success_rate == 100.0
        assert metrics[0].sample_count == 1

    def test_analyze_single_provider_multiple_results(self):
        """Test analyzing multiple results for one provider."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=40.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="8.8.8.8",
                domain="github.com",
                latency_ms=50.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="8.8.8.8",
                domain="example.com",
                latency_ms=60.0,
                success=True,
                error=None,
            ),
        ]
        analyzer = ResultsAnalyzer(results)
        metrics = analyzer.analyze()

        assert len(metrics) == 1
        assert metrics[0].provider == "8.8.8.8"
        assert metrics[0].avg_latency == 50.0
        assert metrics[0].median_latency == 50.0
        assert metrics[0].success_rate == 100.0
        assert metrics[0].sample_count == 3

    def test_analyze_multiple_providers(self):
        """Test analyzing results for multiple providers."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=45.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="1.1.1.1",
                domain="google.com",
                latency_ms=35.0,
                success=True,
                error=None,
            ),
        ]
        analyzer = ResultsAnalyzer(results)
        metrics = analyzer.analyze()

        assert len(metrics) == 2
        providers = {m.provider for m in metrics}
        assert "8.8.8.8" in providers
        assert "1.1.1.1" in providers

    def test_analyze_sorted_by_latency(self):
        """Test that results are sorted by average latency (fastest first)."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=60.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="1.1.1.1",
                domain="google.com",
                latency_ms=30.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="9.9.9.9",
                domain="google.com",
                latency_ms=45.0,
                success=True,
                error=None,
            ),
        ]
        analyzer = ResultsAnalyzer(results)
        metrics = analyzer.analyze()

        assert metrics[0].provider == "1.1.1.1"
        assert metrics[0].avg_latency == 30.0
        assert metrics[1].provider == "9.9.9.9"
        assert metrics[1].avg_latency == 45.0
        assert metrics[2].provider == "8.8.8.8"
        assert metrics[2].avg_latency == 60.0

    def test_analyze_with_failures(self):
        """Test analyzing results with failures."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=45.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="8.8.8.8",
                domain="invalid.test",
                latency_ms=5000.0,
                success=False,
                error="Timeout",
            ),
        ]
        analyzer = ResultsAnalyzer(results)
        metrics = analyzer.analyze()

        assert len(metrics) == 1
        assert metrics[0].provider == "8.8.8.8"
        assert metrics[0].avg_latency == 2522.5
        assert metrics[0].success_rate == 50.0
        assert metrics[0].sample_count == 2

    def test_analyze_all_failures(self):
        """Test analyzing results with all failures."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="invalid1.test",
                latency_ms=5000.0,
                success=False,
                error="Timeout",
            ),
            BenchmarkResult(
                provider="8.8.8.8",
                domain="invalid2.test",
                latency_ms=5000.0,
                success=False,
                error="Timeout",
            ),
        ]
        analyzer = ResultsAnalyzer(results)
        metrics = analyzer.analyze()

        assert len(metrics) == 1
        assert metrics[0].provider == "8.8.8.8"
        assert metrics[0].avg_latency == 5000.0
        assert metrics[0].success_rate == 0.0
        assert metrics[0].sample_count == 2

    def test_analyze_median_calculation_odd_count(self):
        """Test median calculation with odd number of results."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="test1.com",
                latency_ms=10.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="8.8.8.8",
                domain="test2.com",
                latency_ms=50.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="8.8.8.8",
                domain="test3.com",
                latency_ms=90.0,
                success=True,
                error=None,
            ),
        ]
        analyzer = ResultsAnalyzer(results)
        metrics = analyzer.analyze()

        assert metrics[0].median_latency == 50.0

    def test_analyze_median_calculation_even_count(self):
        """Test median calculation with even number of results."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="test1.com",
                latency_ms=10.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="8.8.8.8",
                domain="test2.com",
                latency_ms=30.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="8.8.8.8",
                domain="test3.com",
                latency_ms=70.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="8.8.8.8",
                domain="test4.com",
                latency_ms=90.0,
                success=True,
                error=None,
            ),
        ]
        analyzer = ResultsAnalyzer(results)
        metrics = analyzer.analyze()

        assert metrics[0].median_latency == 50.0

    def test_analyze_complex_scenario(self):
        """Test analyzing complex scenario with multiple providers and mixed results."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=40.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="8.8.8.8",
                domain="github.com",
                latency_ms=50.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="8.8.8.8",
                domain="invalid.test",
                latency_ms=5000.0,
                success=False,
                error="Timeout",
            ),
            BenchmarkResult(
                provider="1.1.1.1",
                domain="google.com",
                latency_ms=25.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="1.1.1.1",
                domain="github.com",
                latency_ms=35.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="1.1.1.1",
                domain="example.com",
                latency_ms=30.0,
                success=True,
                error=None,
            ),
        ]
        analyzer = ResultsAnalyzer(results)
        metrics = analyzer.analyze()

        assert len(metrics) == 2

        cloudflare = next(m for m in metrics if m.provider == "1.1.1.1")
        assert cloudflare.avg_latency == 30.0
        assert cloudflare.success_rate == 100.0
        assert cloudflare.sample_count == 3

        google = next(m for m in metrics if m.provider == "8.8.8.8")
        assert google.success_rate < 100.0
        assert google.sample_count == 3

        assert metrics[0].provider == "1.1.1.1"


class TestDisplayResults:
    """Test display_results function."""

    def test_display_results_empty_list(self):
        """Test displaying empty results list."""
        results = []
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True)

        display_results(results, console=console)

        output = string_io.getvalue()
        assert "No results to display" in output

    def test_display_results_single_provider(self):
        """Test displaying results for single provider."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=45.0,
                success=True,
                error=None,
            )
        ]
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True)

        display_results(results, console=console)

        output = string_io.getvalue()
        assert "8.8.8.8" in output
        assert "45.00" in output
        assert "100.0%" in output
        assert "Summary" in output
        assert "Fastest provider" in output
        assert "Most reliable provider" in output

    def test_display_results_multiple_providers(self):
        """Test displaying results for multiple providers."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=60.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="1.1.1.1",
                domain="google.com",
                latency_ms=30.0,
                success=True,
                error=None,
            ),
        ]
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True)

        display_results(results, console=console)

        output = string_io.getvalue()
        assert "8.8.8.8" in output
        assert "1.1.1.1" in output
        assert "DNS Provider Performance Analysis" in output

    def test_display_results_default_console(self):
        """Test displaying results with default console."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=45.0,
                success=True,
                error=None,
            )
        ]

        display_results(results)

    def test_display_results_identifies_fastest(self):
        """Test that fastest provider is correctly identified."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=60.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="1.1.1.1",
                domain="google.com",
                latency_ms=30.0,
                success=True,
                error=None,
            ),
        ]
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True)

        display_results(results, console=console)

        output = string_io.getvalue()
        assert (
            "Fastest provider: 1.1.1.1" in output
            or "1.1.1.1" in output.split("Fastest")[1].split("\n")[0]
        )

    def test_display_results_identifies_most_reliable(self):
        """Test that most reliable provider is correctly identified."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=30.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="8.8.8.8",
                domain="github.com",
                latency_ms=5000.0,
                success=False,
                error="Timeout",
            ),
            BenchmarkResult(
                provider="1.1.1.1",
                domain="google.com",
                latency_ms=40.0,
                success=True,
                error=None,
            ),
            BenchmarkResult(
                provider="1.1.1.1",
                domain="github.com",
                latency_ms=45.0,
                success=True,
                error=None,
            ),
        ]
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True)

        display_results(results, console=console)

        output = string_io.getvalue()
        assert (
            "Most reliable provider: 1.1.1.1" in output
            or "1.1.1.1" in output.split("Most reliable")[1].split("\n")[0]
        )

    def test_display_results_contains_required_columns(self):
        """Test that table contains all required columns."""
        results = [
            BenchmarkResult(
                provider="8.8.8.8",
                domain="google.com",
                latency_ms=45.0,
                success=True,
                error=None,
            )
        ]
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=True)

        display_results(results, console=console)

        output = string_io.getvalue()
        assert "Provider IP" in output
        assert "Avg Latency (ms)" in output
        assert "Success Rate" in output
        assert "Tests Performed" in output
