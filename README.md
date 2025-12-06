# dns-bench

An asyncio-based DNS benchmarking playground. The CLI iterates across multiple providers and domains, dispatching lookups concurrently while applying retries, exponential backoff, and structured logging.

## Usage

```bash
python -m dns_bench run --iterations 5
```

Key options:

- `--concurrency`: concurrent in-flight lookups (default 10)
- `--timeout`: per-query timeout in seconds (default 1.5 s)
- `--max-retries`: capped retries per query when throttled/failing
- `--providers`: provider keys to include (run `python -m dns_bench run --list-providers` for options)
- `--domains`: domains to benchmark (defaults to a curated list)
- `--json-out` / `--csv-out`: persist raw measurements

The CLI logs each measurement as a JSON payload that includes the provider, domain, latency, retry count, and error metadata where applicable.
