import time
import concurrent.futures
from src.dns_bench.benchmark import BenchmarkRunner

providers = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
domains = ["google.com", "example.com", "github.com", "cloudflare.com"] * 5

runner = BenchmarkRunner(providers=providers, domains=domains, timeout=2.0, iterations=5)

start = time.perf_counter()
results = runner.run()
end = time.perf_counter()

print(f"Time taken: {end - start:.4f}s")
print(f"Results: {len(results)}")
