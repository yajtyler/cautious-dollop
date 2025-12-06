"""Tests for configuration module."""

import pytest

from dns_bench.config.models import Config, DNSProvider, Domain, BenchmarkConfig


def test_dns_provider_creation():
    """Test creating a DNS provider."""
    provider = DNSProvider(
        name="Google",
        primary_ip="8.8.8.8",
        secondary_ip="8.8.4.4",
        category="public"
    )
    assert provider.name == "Google"
    assert provider.primary_ip == "8.8.8.8"
    assert provider.secondary_ip == "8.8.4.4"


def test_domain_creation():
    """Test creating a domain."""
    domain = Domain(
        name="example.com",
        category="general",
        record_type="A"
    )
    assert domain.name == "example.com"
    assert domain.category == "general"
    assert domain.record_type == "A"


def test_config_defaults():
    """Test config with default values."""
    config = Config()
    assert config.version == "1.0.0"
    assert config.providers == []
    assert config.domains == []
    assert config.benchmark.timeout == 5.0
    assert config.output.format == "json"


def test_config_with_providers_and_domains():
    """Test config with providers and domains."""
    provider = DNSProvider(
        name="Google",
        primary_ip="8.8.8.8",
    )
    domain = Domain(name="example.com")

    config = Config(
        providers=[provider],
        domains=[domain]
    )

    assert len(config.providers) == 1
    assert len(config.domains) == 1
    assert config.providers[0].name == "Google"
    assert config.domains[0].name == "example.com"
