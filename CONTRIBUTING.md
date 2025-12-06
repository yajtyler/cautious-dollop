# Contributing to DNS Benchmark Tool

Thank you for your interest in contributing to the DNS Benchmark Tool! This document provides comprehensive guidelines for contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Code Architecture](#code-architecture)
- [Key Modules](#key-modules)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Community Guidelines](#community-guidelines)

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- pip (Python package manager)
- Virtual environment (recommended)

### Initial Setup

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/your-username/dns-benchmark.git
cd dns-benchmark

# 3. Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install development dependencies
pip install -r requirements-dev.txt

# 5. Install the package in development mode
pip install -e .

# 6. Run initial tests to verify setup
pytest

# 7. Install pre-commit hooks
pre-commit install
```

### Development Dependencies

The `requirements-dev.txt` includes:

```txt
# Core dependencies
dnspython>=2.2.0
requests>=2.28.0
pyyaml>=6.0
click>=8.1.0
rich>=12.0.0

# Development tools
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=0.991
pre-commit>=2.20.0
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0
```

## Project Structure

```
dns-benchmark/
├── dns_benchmark/              # Main package directory
│   ├── __init__.py            # Package initialization
│   ├── cli.py                 # Command-line interface
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── benchmark.py       # Main benchmark engine
│   │   ├── dns_client.py      # DNS query client
│   │   ├── metrics.py         # Metrics calculation
│   │   └── providers.py       # DNS provider management
│   ├── config/                # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py        # Configuration loader
│   │   └── validation.py      # Configuration validation
│   ├── output/                # Output formatting
│   │   ├── __init__.py
│   │   ├── formatter.py       # Result formatting
│   │   ├── table.py           # Table output
│   │   ├── json_output.py     # JSON output
│   │   └── csv_output.py      # CSV output
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── network.py         # Network utilities
│       ├── logging.py         # Logging setup
│       └── helpers.py         # General helpers
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── unit/                  # Unit tests
│   │   ├── test_benchmark.py
│   │   ├── test_dns_client.py
│   │   ├── test_metrics.py
│   │   └── test_providers.py
│   ├── integration/           # Integration tests
│   │   ├── test_cli.py
│   │   └── test_end_to_end.py
│   └── fixtures/              # Test data
│       ├── providers.yaml
│       └── sample_results.json
├── docs/                      # Documentation
│   ├── api/                   # API documentation
│   ├── guides/                # User guides
│   └── examples/              # Code examples
├── scripts/                   # Utility scripts
│   ├── update_providers.py    # Update DNS provider list
│   └── generate_docs.py       # Documentation generation
├── .github/                   # GitHub configuration
│   ├── workflows/             # CI/CD workflows
│   │   ├── test.yml
│   │   └── release.yml
│   └── ISSUE_TEMPLATE/        # Issue templates
├── requirements.txt           # Runtime dependencies
├── requirements-dev.txt       # Development dependencies
├── setup.py                   # Package setup
├── pyproject.toml            # Modern Python packaging
├── README.md                  # Project documentation
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE                    # License file
├── CHANGELOG.md               # Version history
├── .gitignore                 # Git ignore rules
├── .pre-commit-config.yaml    # Pre-commit hooks
└── Makefile                   # Common tasks
```

## Code Architecture

### Core Components

#### 1. Benchmark Engine (`core/benchmark.py`)

The main orchestrator that coordinates DNS testing:

```python
class BenchmarkEngine:
    """Main benchmark engine that orchestrates DNS testing"""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.dns_client = DNSClient(config.dns_settings)
        self.metrics_calculator = MetricsCalculator()
    
    async def run_benchmark(self, providers: List[Provider]) -> BenchmarkResult:
        """Run benchmark against specified providers"""
        pass
    
    def generate_report(self, results: BenchmarkResult) -> Report:
        """Generate formatted report from results"""
        pass
```

#### 2. DNS Client (`core/dns_client.py`)

Handles DNS queries with rate limiting and error handling:

```python
class DNSClient:
    """DNS query client with rate limiting and retry logic"""
    
    def __init__(self, settings: DNSSettings):
        self.settings = settings
        self.rate_limiter = RateLimiter(settings.rate_limit)
    
    async def query_provider(self, provider: Provider, domain: str) -> QueryResult:
        """Execute DNS query against specific provider"""
        pass
    
    def batch_query(self, queries: List[Query]) -> List[QueryResult]:
        """Execute multiple queries in parallel"""
        pass
```

#### 3. Metrics Calculator (`core/metrics.py`)

Calculates performance metrics from query results:

```python
class MetricsCalculator:
    """Calculates performance metrics from DNS query results"""
    
    def calculate_latency_stats(self, results: List[QueryResult]) -> LatencyStats:
        """Calculate latency statistics"""
        pass
    
    def calculate_success_rate(self, results: List[QueryResult]) -> float:
        """Calculate success rate percentage"""
        pass
    
    def calculate_stability_score(self, results: List[QueryResult]) -> float:
        """Calculate stability score based on consistency"""
        pass
    
    def calculate_overall_score(self, metrics: ProviderMetrics) -> float:
        """Calculate weighted overall score"""
        pass
```

#### 4. Provider Management (`core/providers.py`)

Manages DNS provider information and selection:

```python
class ProviderManager:
    """Manages DNS provider information and selection"""
    
    def __init__(self, config_path: str):
        self.providers = self._load_providers(config_path)
    
    def get_provider(self, identifier: str) -> Provider:
        """Get provider by identifier"""
        pass
    
    def get_all_providers(self) -> List[Provider]:
        """Get all configured providers"""
        pass
    
    def update_provider_list(self) -> None:
        """Update provider list from remote source"""
        pass
```

### Configuration System

#### Settings Structure (`config/settings.py`)

```python
@dataclass
class BenchmarkConfig:
    """Main configuration class"""
    queries: int = 25
    timeout: float = 3.0
    threads: int = 5
    domains: List[str] = field(default_factory=list)
    output_format: str = "table"
    verbose: bool = False
    
@dataclass
class DNSSettings:
    """DNS-specific configuration"""
    rate_limit: RateLimitConfig
    retry_policy: RetryConfig
    ipv6_enabled: bool = False
```

#### Configuration Validation (`config/validation.py`)

```python
class ConfigValidator:
    """Validates configuration settings"""
    
    def validate_benchmark_config(self, config: BenchmarkConfig) -> List[ValidationError]:
        """Validate benchmark configuration"""
        pass
    
    def validate_provider_config(self, providers: List[Provider]) -> List[ValidationError]:
        """Validate provider configuration"""
        pass
```

### Output System

#### Formatters (`output/formatter.py`)

```python
class OutputFormatter:
    """Base class for output formatters"""
    
    def format_results(self, results: BenchmarkResult) -> str:
        """Format benchmark results"""
        raise NotImplementedError

class TableFormatter(OutputFormatter):
    """Table output formatter"""
    
    def format_results(self, results: BenchmarkResult) -> str:
        """Format results as table"""
        pass

class JSONFormatter(OutputFormatter):
    """JSON output formatter"""
    
    def format_results(self, results: BenchmarkResult) -> str:
        """Format results as JSON"""
        pass
```

## Key Modules

### 1. CLI Module (`cli.py`)

Command-line interface built with Click:

```python
import click
from .core.benchmark import BenchmarkEngine
from .config.settings import BenchmarkConfig

@click.command()
@click.option('--queries', default=25, help='Number of queries per provider')
@click.option('--timeout', default=3.0, help='Query timeout in seconds')
@click.option('--providers', help='Comma-separated list of DNS providers')
@click.pass_context
def main(ctx, queries, timeout, providers):
    """DNS Benchmark Tool - Compare DNS provider performance"""
    config = BenchmarkConfig(queries=queries, timeout=timeout)
    engine = BenchmarkEngine(config)
    results = engine.run_benchmark()
    click.echo(results)
```

### 2. Network Utilities (`utils/network.py`)

Network-related helper functions:

```python
def check_connectivity(host: str, port: int = 53) -> bool:
    """Check network connectivity to host"""
    pass

def get_local_dns_servers() -> List[str]:
    """Get system's configured DNS servers"""
    pass

def test_dns_resolution(domain: str) -> bool:
    """Test if domain can be resolved"""
    pass
```

### 3. Logging Setup (`utils/logging.py`)

Centralized logging configuration:

```python
def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Setup logging configuration"""
    pass

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    pass
```

## Development Workflow

### 1. Branch Strategy

- `main`: Stable, production-ready code
- `develop`: Integration branch for new features
- `feature/*`: Feature development branches
- `bugfix/*`: Bug fix branches
- `release/*`: Release preparation branches

### 2. Feature Development

```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/new-metric

# 2. Make changes
# ... write code ...

# 3. Run tests
pytest
pytest --cov=dns_benchmark

# 4. Run linting and formatting
black dns_benchmark/
flake8 dns_benchmark/
mypy dns_benchmark/

# 5. Commit changes
git add .
git commit -m "feat: add new stability metric calculation"

# 6. Push and create PR
git push origin feature/new-metric
# Create pull request on GitHub
```

### 3. Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting, no functional changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(metrics): add jitter calculation for stability score

Fixes #123

The new jitter metric measures the variation in response times
to better assess DNS provider stability.

- Calculate standard deviation of latencies
- Normalize to 0-100 scale
- Include in overall stability score
```

## Coding Standards

### 1. Code Style

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) and use Black for formatting:

```python
# Good
def calculate_metrics(results: List[QueryResult]) -> Metrics:
    """Calculate performance metrics from query results."""
    if not results:
        raise ValueError("No results provided")
    
    latencies = [r.latency for r in results if r.success]
    return Metrics(
        avg_latency=sum(latencies) / len(latencies),
        success_rate=len([r for r in results if r.success]) / len(results),
    )

# Bad
def calculateMetrics(results):
    if len(results)==0:
        return None
    avg=sum([r.latency for r in results])/len(results)
    return avg
```

### 2. Type Hints

Use type hints for all public functions and methods:

```python
from typing import List, Optional, Dict, Any
import dns.resolver

class DNSClient:
    def __init__(self, timeout: float = 3.0) -> None:
        self.timeout = timeout
        self._resolver = dns.resolver.Resolver()
        self._resolver.timeout = timeout
    
    async def query(
        self, 
        domain: str, 
        record_type: str = "A"
    ) -> Optional[QueryResult]:
        """Query DNS for domain record."""
        try:
            result = await self._resolver.resolve(domain, record_type)
            return QueryResult.from_dns_result(result)
        except Exception as e:
            logger.error(f"DNS query failed for {domain}: {e}")
            return None
```

### 3. Documentation

Docstrings follow Google style:

```python
def calculate_stability_score(
    latency_results: List[float], 
    success_rate: float,
    time_window: float = 300.0
) -> float:
    """Calculate stability score based on latency variance and success rate.
    
    Args:
        latency_results: List of latency measurements in milliseconds.
        success_rate: Overall success rate as percentage (0-100).
        time_window: Time window in seconds for stability calculation.
    
    Returns:
        Stability score as percentage (0-100).
    
    Raises:
        ValueError: If latency_results is empty or contains invalid values.
    
    Example:
        >>> latencies = [12.5, 13.1, 12.8, 13.0, 12.9]
        >>> score = calculate_stability_score(latencies, 98.5)
        >>> print(f"Stability: {score:.1f}%")
        Stability: 94.2%
    """
    if not latency_results:
        raise ValueError("Latency results cannot be empty")
    
    # Implementation...
    return stability_score
```

### 4. Error Handling

Use specific exceptions and proper error handling:

```python
class DNSBenchmarkError(Exception):
    """Base exception for DNS benchmark errors."""
    pass

class ProviderNotFoundError(DNSBenchmarkError):
    """Raised when a DNS provider is not found."""
    pass

class ConfigurationError(DNSBenchmarkError):
    """Raised when configuration is invalid."""
    pass

def get_provider(provider_id: str) -> Provider:
    """Get DNS provider by ID.
    
    Args:
        provider_id: Unique identifier for the provider.
    
    Returns:
        Provider instance.
    
    Raises:
        ProviderNotFoundError: If provider is not found.
    """
    try:
        return PROVIDER_REGISTRY[provider_id]
    except KeyError:
        raise ProviderNotFoundError(f"Provider '{provider_id}' not found")
```

## Testing Guidelines

### 1. Test Structure

Tests are organized by type and module:

```python
# tests/unit/test_metrics.py
import pytest
from dns_benchmark.core.metrics import MetricsCalculator

class TestMetricsCalculator:
    """Test cases for MetricsCalculator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.calculator = MetricsCalculator()
        self.sample_results = [
            QueryResult(latency=12.5, success=True),
            QueryResult(latency=13.1, success=True),
            QueryResult(latency=12.8, success=False),
        ]
    
    def test_calculate_average_latency(self):
        """Test average latency calculation."""
        avg = self.calculator.calculate_average_latency(self.sample_results)
        assert avg == pytest.approx(12.8, rel=1e-1)
    
    def test_calculate_success_rate(self):
        """Test success rate calculation."""
        rate = self.calculator.calculate_success_rate(self.sample_results)
        assert rate == pytest.approx(66.67, rel=1e-1)
    
    @pytest.mark.parametrize("results,expected", [
        ([], 0.0),  # Empty results
        ([QueryResult(latency=10.0, success=True)], 100.0),  # Single success
    ])
    def test_success_rate_edge_cases(self, results, expected):
        """Test success rate with edge cases."""
        rate = self.calculator.calculate_success_rate(results)
        assert rate == expected
```

### 2. Test Coverage

Maintain >90% test coverage:

```bash
# Run tests with coverage
pytest --cov=dns_benchmark --cov-report=html --cov-report=term-missing

# Check coverage thresholds
pytest --cov=dns_benchmark --cov-fail-under=90
```

### 3. Integration Tests

Test end-to-end functionality:

```python
# tests/integration/test_end_to_end.py
import pytest
from dns_benchmark.cli import main
from click.testing import CliRunner

class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_basic_benchmark(self):
        """Test basic benchmark execution."""
        runner = CliRunner()
        result = runner.invoke(main, ['--queries', '5', '--domains', 'google.com'])
        
        assert result.exit_code == 0
        assert 'Provider Results' in result.output
        assert '1.1.1.1' in result.output or '8.8.8.8' in result.output
    
    def test_json_output(self):
        """Test JSON output format."""
        runner = CliRunner()
        result = runner.invoke(main, ['--format', 'json', '--queries', '3'])
        
        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert 'providers' in data
        assert 'overall_score' in data
```

### 4. Fixtures and Mocks

Use fixtures for consistent test data:

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_dns_client():
    """Mock DNS client for testing."""
    client = Mock()
    client.query_provider.return_value = QueryResult(
        latency=12.5, 
        success=True, 
        provider_id="test_provider"
    )
    return client

@pytest.fixture
def sample_providers():
    """Sample DNS providers for testing."""
    return [
        Provider(id="cloudflare", name="Cloudflare", ips=["1.1.1.1"]),
        Provider(id="google", name="Google", ips=["8.8.8.8"]),
    ]
```

## Documentation

### 1. API Documentation

Use Sphinx for API documentation:

```python
# dns_benchmark/core/benchmark.py
class BenchmarkEngine:
    """Main benchmark engine for DNS performance testing.
    
    This class orchestrates the entire benchmark process, from DNS queries
    to metrics calculation and report generation.
    
    Attributes:
        config: Benchmark configuration settings.
        dns_client: DNS client for executing queries.
        metrics_calculator: Calculator for performance metrics.
    
    Example:
        >>> config = BenchmarkConfig(queries=10, timeout=5.0)
        >>> engine = BenchmarkEngine(config)
        >>> results = await engine.run_benchmark(providers)
        >>> report = engine.generate_report(results)
    """
```

### 2. User Documentation

Maintain user guides in the `docs/` directory:

```markdown
# docs/guides/advanced-configuration.md

# Advanced Configuration

This guide covers advanced configuration options for power users.

## Custom Provider Configuration

You can add custom DNS providers by editing your configuration file...

## Performance Tuning

Fine-tune the benchmark for your specific use case...
```

### 3. Code Examples

Provide practical examples:

```python
# docs/examples/custom_metrics.py
"""Example: Calculate custom metrics from benchmark results."""

from dns_benchmark import BenchmarkEngine, BenchmarkConfig

def custom_analysis():
    """Perform custom analysis on DNS benchmark results."""
    config = BenchmarkConfig(queries=50, domains=['example.com'])
    engine = BenchmarkEngine(config)
    
    results = engine.run_benchmark()
    
    # Custom analysis
    fastest_providers = sorted(
        results.providers, 
        key=lambda p: p.avg_latency
    )[:3]
    
    print("Top 3 fastest providers:")
    for provider in fastest_providers:
        print(f"{provider.name}: {provider.avg_latency:.2f}ms")
```

## Submitting Changes

### 1. Pull Request Process

1. **Create PR**: Create a pull request from your feature branch to `develop`
2. **Description**: Provide clear description of changes and motivation
3. **Tests**: Ensure all tests pass and coverage is maintained
4. **Documentation**: Update relevant documentation
5. **Review**: Respond to reviewer feedback promptly

### 2. PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Test coverage maintained

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Changelog updated
```

### 3. Code Review Guidelines

When reviewing code:

1. **Functionality**: Does the code work as intended?
2. **Style**: Does it follow project conventions?
3. **Tests**: Are tests comprehensive and appropriate?
4. **Documentation**: Is the code well-documented?
5. **Performance**: Are there performance implications?
6. **Security**: Are there security considerations?

## Community Guidelines

### 1. Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

### 2. Communication

- Use GitHub issues for bug reports and feature requests
- Use discussions for questions and general topics
- Be patient with maintainers and contributors

### 3. Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Annual contributor highlights

Thank you for contributing to the DNS Benchmark Tool! Your contributions help make DNS performance analysis accessible to everyone.