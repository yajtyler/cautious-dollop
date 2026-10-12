import time
from dns_bench.benchmark import BenchmarkRunner

providers = ["8.8.8.8", "1.1.1.1", "9.9.9.9", "invalid_ip", "192.168.1.1"]
domains = ["example.com", "google.com"]
runner = BenchmarkRunner(providers, domains, iterations=10)

start = time.perf_counter()
# Not calling run() as it connects to real network and could be slow/unstable.
# We will just time the _query_dns method (or map it).
# But doing network requests in the benchmark will hide CPU time.
# Let's mock _get_resolver and resolve to be fast.

class MockResolver:
    def resolve(self, *args, **kwargs):
        pass

runner._get_resolver = lambda p: MockResolver()

# Measure just the loop overhead for _query_dns
start = time.perf_counter()
for _ in range(100):
    for p in providers:
        for d in domains:
            runner._query_dns(p, d)
end = time.perf_counter()
print(f"Time taken: {end - start:.5f}s")
