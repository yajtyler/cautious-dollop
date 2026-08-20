import time
from typing import List
from dataclasses import dataclass
import operator

try:
    import pandas as pd
except ImportError:
    pd = None

@dataclass
class BenchmarkResult:
    provider: str
    domain: str
    latency_ms: float
    success: bool
    error: str = None

def analyze_original(results: List[BenchmarkResult]):
    df = pd.DataFrame(
        {
            "provider": [r.provider for r in results],
            "latency_ms": [r.latency_ms for r in results],
            "success": [r.success for r in results],
        }
    )
    return df

def analyze_vars(results: List[BenchmarkResult]):
    df = pd.DataFrame([vars(r) for r in results])
    return df

def analyze_attrgetter(results: List[BenchmarkResult]):
    get_provider = operator.attrgetter('provider')
    get_latency = operator.attrgetter('latency_ms')
    get_success = operator.attrgetter('success')
    df = pd.DataFrame(
        {
            "provider": [get_provider(r) for r in results],
            "latency_ms": [get_latency(r) for r in results],
            "success": [get_success(r) for r in results],
        }
    )
    return df

def analyze_single_loop_lists(results: List[BenchmarkResult]):
    providers = []
    latencies = []
    successes = []
    for r in results:
        providers.append(r.provider)
        latencies.append(r.latency_ms)
        successes.append(r.success)
    df = pd.DataFrame(
        {
            "provider": providers,
            "latency_ms": latencies,
            "success": successes,
        }
    )
    return df

def analyze_from_records_tuples(results: List[BenchmarkResult]):
    df = pd.DataFrame.from_records(
        [(r.provider, r.latency_ms, r.success) for r in results],
        columns=["provider", "latency_ms", "success"]
    )
    return df

def run_benchmark():
    if pd is None:
        print("Skipping benchmark due to missing pandas dependency")
        return

    count = 100_000
    results = [
        BenchmarkResult(
            provider=f"provider_{i % 10}",
            domain="example.com",
            latency_ms=10.0 + (i % 100),
            success=True
        )
        for i in range(count)
    ]

    methods = [
        ("Original", analyze_original),
        ("Vars (list of dicts)", analyze_vars),
        ("Attrgetter", analyze_attrgetter),
        ("Single loop (append)", analyze_single_loop_lists),
        ("From records (tuples)", analyze_from_records_tuples),
    ]

    # Warmup
    for name, func in methods:
        func(results)

    for name, func in methods:
        start = time.perf_counter()
        for _ in range(10):
            func(results)
        end = time.perf_counter()
        avg_time = (end - start) / 10
        print(f"{name:25} avg time: {avg_time:.4f}s")

if __name__ == "__main__":
    run_benchmark()
