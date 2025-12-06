"""Cross-platform DNS resolver detection utility."""

import platform
import re
import subprocess
from ipaddress import AddressValueError, IPv4Address, IPv6Address
from pathlib import Path
from typing import List, Set


def _is_valid_ip(ip: str) -> bool:
    """
    Validate if a string is a valid IPv4 or IPv6 address.

    Args:
        ip: IP address string to validate

    Returns:
        True if valid IP address, False otherwise
    """
    try:
        IPv4Address(ip)
        return True
    except (AddressValueError, ValueError):
        pass

    try:
        IPv6Address(ip)
        return True
    except (AddressValueError, ValueError):
        pass

    return False


def _parse_linux_resolvers() -> List[str]:
    """
    Parse DNS resolvers from /etc/resolv.conf on Linux.

    Returns:
        List of DNS resolver IP addresses
    """
    resolvers = []
    resolv_conf = Path("/etc/resolv.conf")

    try:
        if resolv_conf.exists():
            with open(resolv_conf, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("nameserver"):
                        parts = line.split()
                        if len(parts) >= 2:
                            ip = parts[1]
                            if _is_valid_ip(ip):
                                resolvers.append(ip)
    except (OSError, IOError, PermissionError):
        pass

    return resolvers


def _parse_macos_resolvers() -> List[str]:
    """
    Parse DNS resolvers from scutil --dns on macOS.

    Returns:
        List of DNS resolver IP addresses
    """
    resolvers = []

    try:
        result = subprocess.run(
            ["scutil", "--dns"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if result.returncode == 0:
            for line in result.stdout.splitlines():
                line = line.strip()
                if "nameserver" in line.lower():
                    parts = line.split(":", 1)
                    if len(parts) >= 2:
                        ip = parts[1].strip()
                        if _is_valid_ip(ip):
                            resolvers.append(ip)
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass

    return resolvers


def _parse_windows_resolvers() -> List[str]:
    """
    Parse DNS resolvers from ipconfig /all on Windows.

    Returns:
        List of DNS resolver IP addresses
    """
    resolvers = []

    try:
        result = subprocess.run(
            ["ipconfig", "/all"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if result.returncode == 0:
            dns_pattern = re.compile(r"DNS Servers.*?:\s*(.+)", re.IGNORECASE)

            for line in result.stdout.splitlines():
                match = dns_pattern.search(line)
                if match:
                    ip = match.group(1).strip()
                    if _is_valid_ip(ip):
                        resolvers.append(ip)
                elif line.strip() and not line.startswith(" ") and ":" not in line:
                    continue
                elif line.strip() and resolvers:
                    ip = line.strip()
                    if _is_valid_ip(ip):
                        resolvers.append(ip)
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass

    return resolvers


def _deduplicate_resolvers(resolvers: List[str]) -> List[str]:
    """
    Remove duplicate IP addresses while preserving order.

    Args:
        resolvers: List of IP addresses that may contain duplicates

    Returns:
        List of unique IP addresses in original order
    """
    seen: Set[str] = set()
    unique_resolvers = []

    for resolver in resolvers:
        if resolver not in seen:
            seen.add(resolver)
            unique_resolvers.append(resolver)

    return unique_resolvers


def get_local_resolvers() -> List[str]:
    """
    Detect local DNS resolvers for the current system.

    This function detects DNS resolvers based on the operating system:
    - Linux: Parses /etc/resolv.conf
    - macOS: Uses scutil --dns command
    - Windows: Parses ipconfig /all output

    All detected IPs are validated (IPv4 and IPv6) and deduplicated.
    If detection fails or no resolvers are found, returns ['127.0.0.1'] as fallback.

    Returns:
        List of DNS resolver IP addresses as strings

    Examples:
        >>> resolvers = get_local_resolvers()
        >>> print(resolvers)
        ['8.8.8.8', '1.1.1.1']
    """
    resolvers = []

    try:
        system = platform.system().lower()

        if system == "linux":
            resolvers = _parse_linux_resolvers()
        elif system == "darwin":
            resolvers = _parse_macos_resolvers()
        elif system == "windows":
            resolvers = _parse_windows_resolvers()
    except Exception:
        pass

    resolvers = _deduplicate_resolvers(resolvers)

    if not resolvers:
        resolvers = ["127.0.0.1"]

    return resolvers
