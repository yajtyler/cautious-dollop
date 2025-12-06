from __future__ import annotations

import argparse
import json
import logging
import socket
import sys
from pathlib import Path
from typing import Iterable, List, Sequence

from .detector import (
    DetectionReport,
    ResolverEndpoint,
    detect_resolvers,
    parse_override_addresses,
)

LOGGER = logging.getLogger("local_dns.cli")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect local DNS resolvers and report fallbacks.",
    )
    parser.add_argument(
        "--resolver",
        dest="resolvers",
        action="append",
        default=[],
        help="Manual resolver IP (can be specified multiple times or with commas)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Optional JSON file that contains a 'resolvers' list.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a JSON summary of the detection result.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase logging verbosity (can be supplied multiple times).",
    )
    return parser


def _configure_logging(verbosity: int) -> None:
    if logging.getLogger().handlers:
        return
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def _load_config_overrides(path: Path) -> List[str]:
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError as exc:  # pragma: no cover - user error
        raise ValueError(f"Config file {path} does not exist") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Config file {path} contains invalid JSON: {exc}") from exc

    if isinstance(data, dict):
        resolvers = data.get("resolvers")
        if isinstance(resolvers, list):
            return [str(item) for item in resolvers if str(item).strip()]
    raise ValueError(
        f"Config file {path} must contain a dictionary with a 'resolvers' list"
    )


def _system_api_available() -> bool:
    try:
        socket.getaddrinfo("example.com", 53)
        return True
    except socket.gaierror:
        return False


def _system_resolver_placeholder() -> ResolverEndpoint:
    return ResolverEndpoint(
        address="system-default",
        version=0,
        source="system-api",
        metadata={
            "kind": "system",
            "method": "socket.getaddrinfo",
            "note": "Using OS configured resolvers via getaddrinfo",
        },
    )


def _summarise(
    stage: str,
    report: DetectionReport,
    resolvers: Sequence[ResolverEndpoint],
    manual_overrides: Sequence[ResolverEndpoint],
) -> str:
    payload = {
        "stage": stage,
        "errors": report.errors,
        "resolvers": [resolver.as_dict() for resolver in resolvers],
        "manual_overrides": [resolver.as_dict() for resolver in manual_overrides],
    }
    return json.dumps(payload, indent=2)


def _collect_manual_overrides(args: argparse.Namespace) -> List[ResolverEndpoint]:
    entries: List[str] = list(args.resolvers or [])
    if args.config:
        try:
            entries.extend(_load_config_overrides(args.config))
        except ValueError as exc:
            LOGGER.warning("%s", exc)
    return parse_override_addresses(entries)


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    _configure_logging(args.verbose)

    manual_resolvers = _collect_manual_overrides(args)
    report = detect_resolvers()
    active_resolvers = report.resolvers
    stage = "detected"

    if active_resolvers:
        LOGGER.log(
            logging.INFO if args.verbose else logging.DEBUG,
            "Detected %d resolver(s) from the local system.",
            len(active_resolvers),
        )
    else:
        LOGGER.warning(
            "Local resolver detection failed. Falling back to system APIs (socket.getaddrinfo)."
        )
        if _system_api_available():
            stage = "system"
            active_resolvers = [_system_resolver_placeholder()]
            LOGGER.info("Using OS resolver APIs as a fallback stage.")
        elif manual_resolvers:
            stage = "override"
            active_resolvers = manual_resolvers
            LOGGER.warning(
                "Using manual resolver overrides because automatic detection failed."
            )
        else:
            stage = "none"
            LOGGER.warning(
                "Unable to determine any resolvers. Provide at least one via --resolver or --config."
            )

    if args.summary:
        print(_summarise(stage, report, active_resolvers, manual_resolvers))

    if stage == "none":
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
