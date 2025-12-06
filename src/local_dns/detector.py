from __future__ import annotations

import ipaddress
import platform
import subprocess
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, List, Sequence

CommandRunner = Callable[[Sequence[str]], str]


@dataclass(frozen=True)
class ResolverEndpoint:
    """Represents a nameserver address along with discovery metadata."""

    address: str
    version: int
    source: str
    metadata: dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation of the resolver."""
        return {
            "address": self.address,
            "version": self.version,
            "source": self.source,
            "metadata": dict(self.metadata),
        }


@dataclass
class DetectionReport:
    """Summarises the outcome of a detection pass."""

    resolvers: List[ResolverEndpoint] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "resolvers": [resolver.as_dict() for resolver in self.resolvers],
            "errors": list(self.errors),
        }


@dataclass
class DetectorConfig:
    """Configuration for resolver discovery."""

    resolv_conf: Path = Path("/etc/resolv.conf")
    network_manager_dir: Path = Path("/etc/NetworkManager/system-connections")
    scutil_command: Sequence[str] = ("scutil", "--dns")
    ipconfig_command: Sequence[str] = ("ipconfig", "/all")
    command_runner: CommandRunner | None = None
    os_name: str | None = None


def detect_resolvers(config: DetectorConfig | None = None) -> DetectionReport:
    """Detect resolvers for the active platform."""

    config = config or DetectorConfig()
    errors: List[str] = []
    resolvers: List[ResolverEndpoint] = []
    system_name = (config.os_name or platform.system()).lower()

    try:
        if system_name == "windows":
            resolvers.extend(_detect_from_ipconfig(config, errors))
        elif system_name == "darwin":
            resolvers.extend(_detect_from_scutil(config, errors))
        else:
            resolvers.extend(_detect_from_unix(config, errors))
    except Exception as exc:  # pragma: no cover - safety net
        errors.append(f"Unexpected detection failure: {exc}")

    return DetectionReport(resolvers=_deduplicate(resolvers), errors=errors)


def parse_override_addresses(entries: Iterable[str]) -> List[ResolverEndpoint]:
    """Validate and normalise manual override addresses."""

    resolvers: List[ResolverEndpoint] = []
    for position, raw_entry in enumerate(entries):
        for candidate in _split_candidates(raw_entry):
            resolver = _build_resolver(
                candidate,
                source="manual",
                metadata={"kind": "manual", "position": position},
                errors=None,
            )
            if resolver:
                resolvers.append(resolver)
    return _deduplicate(resolvers)


def _detect_from_unix(config: DetectorConfig, errors: List[str]) -> List[ResolverEndpoint]:
    resolvers: List[ResolverEndpoint] = []
    text = _safe_read_text(config.resolv_conf, errors)
    if text:
        resolvers.extend(
            _parse_resolv_conf_text(
                text, source=str(config.resolv_conf), errors=errors
            )
        )

    network_dir = config.network_manager_dir
    if network_dir.exists():
        resolvers.extend(_collect_network_manager_profiles(network_dir, errors))

    return resolvers


def _detect_from_scutil(config: DetectorConfig, errors: List[str]) -> List[ResolverEndpoint]:
    runner = config.command_runner or _default_runner
    try:
        output = runner(config.scutil_command)
    except FileNotFoundError as exc:
        errors.append(f"scutil not available: {exc}")
        return []
    except subprocess.SubprocessError as exc:
        errors.append(f"scutil invocation failed: {exc}")
        return []
    return _parse_scutil_output(output, errors)


def _detect_from_ipconfig(config: DetectorConfig, errors: List[str]) -> List[ResolverEndpoint]:
    runner = config.command_runner or _default_runner
    try:
        output = runner(config.ipconfig_command)
    except FileNotFoundError as exc:
        errors.append(f"ipconfig not available: {exc}")
        return []
    except subprocess.SubprocessError as exc:
        errors.append(f"ipconfig invocation failed: {exc}")
        return []
    return _parse_ipconfig_output(output, errors)


def _collect_network_manager_profiles(
    directory: Path, errors: List[str]
) -> List[ResolverEndpoint]:
    resolvers: List[ResolverEndpoint] = []
    try:
        files = [path for path in directory.rglob("*") if path.is_file()]
    except (OSError, PermissionError) as exc:
        errors.append(f"Failed to read NetworkManager profiles: {exc}")
        return resolvers

    for path in sorted(files):
        text = _safe_read_text(path, errors)
        if text:
            resolvers.extend(
                _parse_network_manager_file(text, source=str(path), errors=errors)
            )
    return resolvers


def _parse_resolv_conf_text(
    text: str, *, source: str, errors: List[str]
) -> List[ResolverEndpoint]:
    resolvers: List[ResolverEndpoint] = []
    for idx, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        lowered = line.lower()
        if lowered.startswith("nameserver"):
            tokens = line.split()
            if len(tokens) > 1:
                candidate = tokens[1]
                resolver = _build_resolver(
                    candidate,
                    source=source,
                    metadata={"kind": "resolv.conf", "line": idx},
                    errors=errors,
                )
                if resolver:
                    resolvers.append(resolver)
    return resolvers


def _parse_network_manager_file(
    text: str, *, source: str, errors: List[str]
) -> List[ResolverEndpoint]:
    resolvers: List[ResolverEndpoint] = []
    for idx, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(";"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key_lower = key.strip().lower()
        if not key_lower.startswith("dns"):
            continue
        for candidate in _split_candidates(value):
            resolver = _build_resolver(
                candidate,
                source=source,
                metadata={
                    "kind": "network-manager",
                    "line": idx,
                    "key": key.strip(),
                },
                errors=errors,
            )
            if resolver:
                resolvers.append(resolver)
    return resolvers


def _parse_scutil_output(output: str, errors: List[str]) -> List[ResolverEndpoint]:
    resolvers: List[ResolverEndpoint] = []
    current_resolver = "unknown"
    current_interface: str | None = None

    for raw_line in output.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("resolver #"):
            current_resolver = stripped.split("#", 1)[1].strip()
            current_interface = None
            continue
        if stripped.startswith("if_index"):
            current_interface = stripped.split(":", 1)[1].strip()
            continue
        if "nameserver" in stripped and ":" in stripped:
            candidate = stripped.split(":", 1)[1].strip()
            metadata = {"kind": "scutil", "resolver": current_resolver}
            if current_interface:
                metadata["interface"] = current_interface
            resolver = _build_resolver(
                candidate,
                source="scutil --dns",
                metadata=metadata,
                errors=errors,
            )
            if resolver:
                resolvers.append(resolver)
    return resolvers


def _parse_ipconfig_output(output: str, errors: List[str]) -> List[ResolverEndpoint]:
    resolvers: List[ResolverEndpoint] = []
    current_adapter: str | None = None
    collecting_dns = False
    dns_indent: int | None = None

    for raw_line in output.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            collecting_dns = False
            dns_indent = None
            continue

        lowered = stripped.lower()

        if collecting_dns:
            current_indent = len(raw_line) - len(raw_line.lstrip())
            if dns_indent is not None and current_indent > dns_indent:
                resolver = _build_resolver(
                    stripped,
                    source="ipconfig /all",
                    metadata={
                        "kind": "ipconfig",
                        "adapter": current_adapter,
                    },
                    errors=errors,
                )
                if resolver:
                    resolvers.append(resolver)
                continue
            collecting_dns = False
            dns_indent = None

        if lowered.endswith(":") and "adapter" in lowered:
            current_adapter = stripped.rstrip(":")
            continue

        if lowered.startswith("dns servers") and ":" in stripped:
            collecting_dns = True
            dns_indent = len(raw_line) - len(raw_line.lstrip())
            _, rest = stripped.split(":", 1)
            rest = rest.strip()
            if rest:
                for candidate in _split_candidates(rest):
                    resolver = _build_resolver(
                        candidate,
                        source="ipconfig /all",
                        metadata={
                            "kind": "ipconfig",
                            "adapter": current_adapter,
                        },
                        errors=errors,
                    )
                    if resolver:
                        resolvers.append(resolver)
            continue

    return resolvers


def _safe_read_text(path: Path, errors: List[str]) -> str | None:
    try:
        return path.read_text()
    except FileNotFoundError:
        return None
    except PermissionError as exc:
        errors.append(f"Permission denied reading {path}: {exc}")
    except OSError as exc:
        errors.append(f"Failed to read {path}: {exc}")
    return None


def _split_candidates(value: str) -> List[str]:
    sanitized = value.replace(",", " ").replace(";", " ")
    return [candidate.strip() for candidate in sanitized.split() if candidate.strip()]


def _build_resolver(
    candidate: str,
    *,
    source: str,
    metadata: dict[str, object] | None,
    errors: List[str] | None,
) -> ResolverEndpoint | None:
    cleaned = candidate.strip().strip("[]")
    if not cleaned:
        return None
    try:
        ip = ipaddress.ip_address(cleaned)
    except ValueError:
        if errors is not None:
            errors.append(f"Skipping invalid IP '{cleaned}' from {source}")
        return None
    version = 4 if ip.version == 4 else 6
    return ResolverEndpoint(
        address=str(ip),
        version=version,
        source=source,
        metadata=metadata or {},
    )


def _deduplicate(resolvers: Iterable[ResolverEndpoint]) -> List[ResolverEndpoint]:
    ordered: OrderedDict[str, ResolverEndpoint] = OrderedDict()
    for resolver in resolvers:
        ordered.setdefault(resolver.address, resolver)
    return list(ordered.values())


def _default_runner(command: Sequence[str]) -> str:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise subprocess.SubprocessError(
            f"Command {' '.join(command)} failed: {completed.stderr.strip()}"
        )
    return completed.stdout
