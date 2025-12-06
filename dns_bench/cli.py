from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path
from typing import Sequence

from . import __version__
from .config import (
    DEFAULT_BACKOFF_BASE,
    DEFAULT_BACKOFF_JITTER,
    DEFAULT_BACKOFF_MAX,
    DEFAULT_CONCURRENCY,
    DEFAULT_DOMAINS,
    DEFAULT_ITERATIONS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_PROVIDER_KEYS,
    DEFAULT_TIMEOUT,
)
from .engine import BenchmarkEngine
from .exporters import export_csv, export_json
from .providers import build_providers, provider_catalog


def main(argv: Sequence[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "list_providers", False):
        for key in sorted(provider_catalog().keys()):
            print(key)
        return

    if args.command == "run":
        configure_logging(args.verbose)
        try:
            asyncio.run(run_benchmark(args))
        except KeyboardInterrupt:  # pragma: no cover - CLI ergonomics
            raise SystemExit(1)
        except Exception as exc:  # pragma: no cover - CLI fallback
            logging.getLogger("dns_bench").exception("Benchmark failed: %s", exc)
            raise SystemExit(1)
    else:  # pragma: no cover - safety
        parser.print_help()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dns_bench", description="DNS benchmarking toolkit")
    parser.add_argument("--version", action="version", version=f"dns_bench {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Execute the benchmark run")
    run_parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS)
    run_parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    run_parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    run_parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    run_parser.add_argument("--backoff-base", type=float, default=DEFAULT_BACKOFF_BASE)
    run_parser.add_argument("--backoff-max", type=float, default=DEFAULT_BACKOFF_MAX)
    run_parser.add_argument("--backoff-jitter", type=float, default=DEFAULT_BACKOFF_JITTER)
    run_parser.add_argument("--providers", nargs="*", default=None, help="Subset of providers to use")
    run_parser.add_argument(
        "--domains",
        nargs="*",
        default=None,
        help="Domain list to benchmark. Defaults to a curated list.",
    )
    run_parser.add_argument("--json-out", type=Path, default=None, help="Persist measurements to JSON")
    run_parser.add_argument("--csv-out", type=Path, default=None, help="Persist measurements to CSV")
    run_parser.add_argument("--verbose", action="store_true")
    run_parser.add_argument("--list-providers", action="store_true", help="List available providers")

    return parser


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def _resolve_sequence(value: Sequence[str] | None, default: Sequence[str]) -> list[str]:
    return list(value) if value else list(default)


async def run_benchmark(args: argparse.Namespace) -> None:
    providers = build_providers(args.providers or DEFAULT_PROVIDER_KEYS)
    domains = _resolve_sequence(args.domains, DEFAULT_DOMAINS)

    engine = BenchmarkEngine(
        providers=providers,
        domains=domains,
        iterations=max(1, args.iterations),
        concurrency=max(1, args.concurrency),
        query_timeout=max(0.1, args.timeout),
        max_retries=max(0, args.max_retries),
        backoff_base=max(0.0, args.backoff_base),
        backoff_max=max(args.backoff_base, args.backoff_max),
        backoff_jitter=max(0.0, args.backoff_jitter),
    )

    measurements = await engine.run()

    if args.json_out:
        export_json(measurements, args.json_out)
    if args.csv_out:
        export_csv(measurements, args.csv_out)

    logging.getLogger("dns_bench").info("Completed %d measurements", len(measurements))
