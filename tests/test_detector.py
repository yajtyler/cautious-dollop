from __future__ import annotations

import textwrap

from local_dns.detector import (
    DetectorConfig,
    detect_resolvers,
    parse_override_addresses,
)


def test_detect_resolvers_from_resolv_conf(tmp_path):
    resolv_conf = tmp_path / "resolv.conf"
    resolv_conf.write_text(
        """
        # comment
        nameserver 1.1.1.1
        nameserver 2001:4860:4860::8888
        """
    )
    network_dir = tmp_path / "nm"
    network_dir.mkdir()

    config = DetectorConfig(
        resolv_conf=resolv_conf,
        network_manager_dir=network_dir,
        os_name="linux",
    )

    report = detect_resolvers(config=config)
    addresses = {resolver.address for resolver in report.resolvers}

    assert "1.1.1.1" in addresses
    assert "2001:4860:4860::8888" in addresses
    assert report.errors == []


def test_detect_resolvers_from_network_manager(tmp_path):
    network_dir = tmp_path / "nm"
    network_dir.mkdir()
    profile = network_dir / "home.nmconnection"
    profile.write_text(
        """
        [ipv4]
        dns=10.0.0.1; 10.0.0.2
        [ipv6]
        dns=2001:db8::10
        """
    )

    config = DetectorConfig(
        resolv_conf=tmp_path / "resolv.conf",
        network_manager_dir=network_dir,
        os_name="linux",
    )

    report = detect_resolvers(config=config)
    addresses = {resolver.address for resolver in report.resolvers}

    assert {"10.0.0.1", "10.0.0.2", "2001:db8::10"}.issubset(addresses)


def test_detect_resolvers_from_scutil(tmp_path):
    sample = textwrap.dedent(
        """
        DNS configuration

        resolver #1
          nameserver[0] : 8.8.8.8
          if_index : 4 (en0)

        resolver #2
          nameserver[0] : 2001:4860:4860::8888
        """
    )

    config = DetectorConfig(
        resolv_conf=tmp_path / "resolv.conf",
        network_manager_dir=tmp_path / "nm",
        os_name="darwin",
        command_runner=lambda _: sample,
    )

    report = detect_resolvers(config=config)
    addresses = [resolver.address for resolver in report.resolvers]

    assert addresses == ["8.8.8.8", "2001:4860:4860::8888"]


def test_detect_resolvers_from_ipconfig(tmp_path):
    sample = textwrap.dedent(
        """
        Windows IP Configuration

        Ethernet adapter Ethernet:
           Connection-specific DNS Suffix  . :
           DNS Servers . . . . . . . . . . . : 10.0.0.1
                                           1.1.1.1

        Wireless LAN adapter Wi-Fi:
           DNS Servers . . . . . . . . . . . : 2001:4860:4860::8844
        """
    )

    config = DetectorConfig(
        resolv_conf=tmp_path / "resolv.conf",
        network_manager_dir=tmp_path / "nm",
        os_name="windows",
        command_runner=lambda _: sample,
    )

    report = detect_resolvers(config=config)
    addresses = {resolver.address for resolver in report.resolvers}

    assert {"10.0.0.1", "1.1.1.1", "2001:4860:4860::8844"} == addresses


def test_detection_reports_errors_for_invalid_entries(tmp_path):
    resolv_conf = tmp_path / "resolv.conf"
    resolv_conf.write_text("nameserver invalid-ip\nnameserver 9.9.9.9\n")

    config = DetectorConfig(
        resolv_conf=resolv_conf,
        network_manager_dir=tmp_path / "nm",
        os_name="linux",
    )

    report = detect_resolvers(config=config)

    assert [resolver.address for resolver in report.resolvers] == ["9.9.9.9"]
    assert any("invalid-ip" in error for error in report.errors)


def test_parse_override_addresses_deduplicates_entries():
    overrides = parse_override_addresses(["1.1.1.1, 8.8.8.8", "8.8.8.8"])
    assert [resolver.address for resolver in overrides] == ["1.1.1.1", "8.8.8.8"]
