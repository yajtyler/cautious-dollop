import cProfile
import pstats
import io
from src.dns_bench.benchmark import BenchmarkRunner

providers = ["8.8.8.8"]
domains = ["google.com", "example.com"] * 5

runner = BenchmarkRunner(providers=providers, domains=domains, timeout=2.0, iterations=5)

pr = cProfile.Profile()
pr.enable()
runner.run()
pr.disable()

s = io.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats(20)
print(s.getvalue())
