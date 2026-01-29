"""Data models for DNS Benchmark configuration."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DNSProvider(BaseModel):
    """DNS Provider configuration."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Google",
                "primary_ip": "8.8.8.8",
                "secondary_ip": "8.8.4.4",
                "category": "public",
            }
        }
    )

    name: str = Field(..., description="Provider name (e.g., Google, Cloudflare)")
    primary_ip: str = Field(..., description="Primary IP address")
    secondary_ip: Optional[str] = Field(None, description="Secondary IP address")
    category: str = Field("public", description="Provider category (public, enterprise, local)")


class Domain(BaseModel):
    """Domain configuration for benchmarking."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "example.com",
                "category": "general",
                "record_type": "A",
            }
        }
    )

    name: str = Field(..., description="Domain name to query")
    category: str = Field("general", description="Domain category (general, cdn, streaming)")
    record_type: str = Field("A", description="DNS record type to query")


class BenchmarkConfig(BaseModel):
    """Benchmark execution configuration."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timeout": 5.0,
                "retries": 1,
                "concurrent_queries": 10,
                "iterations": 10,
            }
        }
    )

    timeout: float = Field(5.0, description="Query timeout in seconds")
    retries: int = Field(1, description="Number of retries per query")
    concurrent_queries: int = Field(10, description="Number of concurrent queries")
    iterations: int = Field(10, description="Number of iterations per domain per provider")


class OutputConfig(BaseModel):
    """Output configuration."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "format": "json",
                "path": "output/results",
            }
        }
    )

    format: str = Field("json", description="Output format (json, csv, text)")
    path: str = Field("output/results", description="Output path prefix")


class Config(BaseModel):
    """Root configuration for DNS Benchmark."""

    model_config = ConfigDict(json_schema_extra={"title": "DNS Benchmark Configuration"})

    version: str = Field("1.0.0", description="Configuration version")
    providers: list[DNSProvider] = Field(default_factory=list, description="DNS providers")
    domains: list[Domain] = Field(default_factory=list, description="Domains to benchmark")
    benchmark: BenchmarkConfig = Field(default_factory=BenchmarkConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
