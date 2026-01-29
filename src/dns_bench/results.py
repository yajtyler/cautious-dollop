"""Results analysis and display module for DNS benchmarks."""

import statistics
from dataclasses import dataclass
from typing import Any, List, Optional

from rich.console import Console
from rich.table import Table


@dataclass
class ProviderMetrics:
    """Metrics for a single DNS provider."""

    provider: str
    avg_latency: float
    median_latency: float
    success_rate: float
    sample_count: int


class ResultsAnalyzer:
    """
    Analyze benchmark results and compute per-provider metrics.

    Takes raw benchmark results and computes statistics including average latency,
    median latency, success rate, and sample count for each provider.
    """

    def __init__(self, results: List[dict]) -> None:
        """
        Initialize ResultsAnalyzer with raw benchmark results.

        Args:
            results: List of benchmark result dictionaries from BenchmarkRunner
        """
        self.results = results

    def analyze(self) -> List[ProviderMetrics]:
        """
        Analyze results and compute metrics per provider.

        Returns:
            List of ProviderMetrics sorted by average latency (fastest first)
        """
        provider_data: dict[str, dict[str, Any]] = {}

        for result in self.results:
            provider = result["provider"]
            if provider not in provider_data:
                provider_data[provider] = {
                    "latencies": [],
                    "success_count": 0,
                    "total_count": 0,
                }

            provider_data[provider]["latencies"].append(result["latency_ms"])
            provider_data[provider]["total_count"] += 1
            if result["success"]:
                provider_data[provider]["success_count"] += 1

        metrics_list = []
        for provider, data in provider_data.items():
            latencies: List[float] = data["latencies"]
            avg_latency = statistics.mean(latencies)
            median_latency = statistics.median(latencies)
            success_rate = (data["success_count"] / data["total_count"]) * 100
            sample_count = data["total_count"]

            metrics = ProviderMetrics(
                provider=provider,
                avg_latency=avg_latency,
                median_latency=median_latency,
                success_rate=success_rate,
                sample_count=sample_count,
            )
            metrics_list.append(metrics)

        metrics_list.sort(key=lambda m: m.avg_latency)
        return metrics_list


def display_results(results: List[dict], console: Optional[Console] = None) -> None:
    """
    Display benchmark results in a formatted table with summary.

    Args:
        results: List of raw benchmark results from BenchmarkRunner
        console: Optional Rich Console instance (creates new one if not provided)
    """
    if console is None:
        console = Console()

    if not results:
        console.print("[yellow]No results to display[/yellow]")
        return

    analyzer = ResultsAnalyzer(results)
    metrics = analyzer.analyze()

    table = Table(title="DNS Provider Performance Analysis")
    table.add_column("Provider IP", style="cyan", justify="left")
    table.add_column("Avg Latency (ms)", justify="right")
    table.add_column("Success Rate", justify="right")
    table.add_column("Tests Performed", justify="right", style="dim")

    for metric in metrics:
        if metric.avg_latency < 50:
            latency_style = "green"
        elif metric.avg_latency < 100:
            latency_style = "yellow"
        else:
            latency_style = "red"

        table.add_row(
            metric.provider,
            f"[{latency_style}]{metric.avg_latency:.2f}[/{latency_style}]",
            f"{metric.success_rate:.1f}%",
            str(metric.sample_count),
        )

    console.print(table)

    fastest = metrics[0]
    most_reliable = max(metrics, key=lambda m: m.success_rate)

    console.print()
    console.print("[bold]Summary:[/bold]")
    console.print(
        f"  • Fastest provider: [cyan]{fastest.provider}[/cyan] "
        f"({fastest.avg_latency:.2f}ms average latency)"
    )
    console.print(
        f"  • Most reliable provider: [cyan]{most_reliable.provider}[/cyan] "
        f"({most_reliable.success_rate:.1f}% success rate)"
    )
