# DNS Benchmark

A comprehensive DNS resolver benchmarking tool with support for multiple providers and concurrent query execution.

## Features

- **Multi-Provider Support**: Benchmark against multiple DNS providers (Google, Cloudflare, Quad9, OpenDNS, Verisign, and custom)
- **Domain Pool Management**: Configure domain categories for realistic benchmarking scenarios
- **Concurrent Execution**: Efficient async/concurrent query execution
- **CLI Interface**: Rich, user-friendly command-line interface with Click
- **Configuration Management**: YAML/JSON configuration support
- **Testing**: Comprehensive test suite with pytest

## Project Structure

```
dns-bench/
├── src/
│   └── dns_bench/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py                 # CLI entry point
│       ├── config/
│       │   ├── __init__.py
│       │   ├── models.py          # Configuration data models
│       │   └── loader.py          # Configuration file loader
│       └── core/
│           ├── __init__.py
│           └── di.py              # Dependency injection container
├── config/
│   ├── config.yaml                # Default configuration
│   └── config.example.json        # Example JSON configuration
├── tests/
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
├── pyproject.toml                 # Poetry project configuration
└── README.md
```

## Installation

### Requirements

- Python 3.11+
- Poetry (for dependency management)

### Setup

1. Install dependencies using Poetry:

```bash
poetry install
```

2. Verify installation:

```bash
python -m dns_bench --help
```

## Configuration

Configuration is managed through YAML or JSON files. The default configuration is located at `config/config.yaml`.

### Configuration Structure

```yaml
version: "1.0.0"

providers:
  - name: "Provider Name"
    primary_ip: "IP Address"
    secondary_ip: "Optional Secondary IP"
    category: "public|enterprise|local"

domains:
  - name: "example.com"
    category: "general|cdn|streaming"
    record_type: "A|AAAA|MX|etc"

benchmark:
  timeout: 5.0                # Query timeout in seconds
  retries: 1                  # Number of retries
  concurrent_queries: 10      # Concurrent query limit
  iterations: 10              # Iterations per domain

output:
  format: "json|csv|text"
  path: "output/results"
```

### Example Providers

The default configuration includes popular public DNS providers:
- **Google**: 8.8.8.8, 8.8.4.4
- **Cloudflare**: 1.1.1.1, 1.0.0.1
- **Quad9**: 9.9.9.9, 149.112.112.112
- **OpenDNS**: 208.67.222.222, 208.67.220.220
- **Verisign**: 64.6.64.6, 64.6.65.6

### Example Domains

Pre-configured domain categories:
- **General**: example.com, google.com, github.com
- **CDN**: cloudflare.com
- **Streaming**: netflix.com, youtube.com

## Development

### Running Tests

```bash
poetry run pytest
```

### With Coverage

```bash
poetry run pytest --cov=src/dns_bench
```

### Code Quality

The project uses:
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

## Usage

### Display Help

```bash
python -m dns_bench --help
```

### Display Version

```bash
python -m dns_bench version
```

### Custom Configuration

```bash
python -m dns_bench --config /path/to/config.yaml
```

### Verbose Output

```bash
python -m dns_bench --verbose
```

## Dependencies

### Core Dependencies

- **dnspython**: DNS protocol implementation
- **click**: Modern CLI framework
- **rich**: Terminal formatting
- **aiohttp**: Async HTTP client
- **pydantic**: Data validation
- **pyyaml**: YAML parsing

### Development Dependencies

- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **black**: Code formatter
- **isort**: Import sorter
- **flake8**: Linter
- **mypy**: Type checker
- **types-pyyaml**: Type stubs for PyYAML

## License

MIT
