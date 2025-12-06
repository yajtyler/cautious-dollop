# DNS Benchmark Tool

A high-performance DNS benchmarking utility that measures and compares the performance of various DNS providers across multiple metrics including latency, success rate, and stability scores.

## Features

- **Multi-Provider Support**: Tests against a curated list of reliable DNS providers
- **Comprehensive Metrics**: Measures latency, success rate, and stability scores
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Configurable**: Customize test parameters, providers, and domains
- **Detailed Reporting**: Export results in multiple formats (JSON, CSV, plain text)
- **Rate Limiting**: Built-in protection against provider rate limits
- **Real-time Monitoring**: Watch performance metrics update in real-time

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [DNS Providers](#dns-providers)
- [Metrics Explained](#metrics-explained)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Installation

### Prerequisites

- **Python 3.8+** (required)
- **pip** (Python package manager)
- **Internet connection** (for DNS queries)

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python and pip if not already installed
sudo apt install python3 python3-pip

# Clone the repository
git clone https://github.com/your-username/dns-benchmark.git
cd dns-benchmark

# Install dependencies
pip3 install -r requirements.txt

# Install the tool
pip3 install -e .
```

### Linux (CentOS/RHEL/Fedora)

```bash
# Install Python and pip
sudo dnf install python3 python3-pip  # Fedora
# or
sudo yum install python3 python3-pip  # CentOS/RHEL

# Clone the repository
git clone https://github.com/your-username/dns-benchmark.git
cd dns-benchmark

# Install dependencies
pip3 install -r requirements.txt

# Install the tool
pip3 install -e .
```

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python3

# Clone the repository
git clone https://github.com/your-username/dns-benchmark.git
cd dns-benchmark

# Install dependencies
pip3 install -r requirements.txt

# Install the tool
pip3 install -e .
```

### Windows

```powershell
# Install Python from https://python.org (ensure "Add to PATH" is checked)

# Open PowerShell or Command Prompt as Administrator

# Clone the repository
git clone https://github.com/your-username/dns-benchmark.git
cd dns-benchmark

# Install dependencies
pip install -r requirements.txt

# Install the tool
pip install -e .
```

## Quick Start

### Basic Usage

Run a quick benchmark with default settings:

```bash
dns-benchmark
```

This will test against all configured DNS providers using default test domains and provide a summary report.

### Command Examples

```bash
# Run benchmark with 10 queries per test
dns-benchmark --queries 10

# Test specific DNS providers
dns-benchmark --providers "8.8.8.8,1.1.1.1"

# Use custom test domains
dns-benchmark --domains "google.com,cloudflare.com,github.com"

# Export results to JSON
dns-benchmark --output results.json --format json

# Run with verbose output
dns-benchmark --verbose

# Test IPv6 DNS servers
dns-benchmark --ipv6

# Set custom timeout
dns-benchmark --timeout 5

# Run continuous monitoring (updates every 60 seconds)
dns-benchmark --monitor --interval 60
```

### Sample Output

```
DNS Benchmark Results
=====================

Test Configuration:
- Queries per provider: 25
- Test domains: google.com, cloudflare.com, github.com, stackoverflow.com
- Timeout: 3.0 seconds
- Parallel threads: 5

Provider Results:
┌─────────────┬──────────────┬─────────────┬──────────────┬─────────────┐
│ Provider    │ Avg Latency  │ Success Rate│ Stability    │ Overall     │
├─────────────┼──────────────┼─────────────┼──────────────┼─────────────┤
│ 1.1.1.1     │ 12.4ms       │ 100.0%      │ 98.5%        │ 99.2%       │
│ 8.8.8.8     │ 18.7ms       │ 99.2%       │ 96.8%        │ 98.0%       │
│ 9.9.9.9     │ 15.2ms       │ 98.8%       │ 97.2%        │ 98.0%       │
│ 208.67.222.222│ 22.1ms     │ 97.6%       │ 94.3%        │ 95.9%       │
└─────────────┴──────────────┴─────────────┴──────────────┴─────────────┘

Best Overall: 1.1.1.1 (Cloudflare)
Fastest: 1.1.1.1 (12.4ms average)
Most Reliable: 1.1.1.1 (100.0% success rate)

Test completed in 2.34 seconds
```

## Configuration

### Configuration File

Create a `~/.dns-benchmark.yaml` file to customize default settings:

```yaml
# ~/.dns-benchmark.yaml
default:
  queries: 25
  timeout: 3.0
  threads: 5
  domains:
    - google.com
    - cloudflare.com
    - github.com
    - stackoverflow.com
    - wikipedia.org
  
providers:
  cloudflare:
    primary: "1.1.1.1"
    secondary: "1.0.0.1"
    name: "Cloudflare DNS"
  
  google:
    primary: "8.8.8.8"
    secondary: "8.8.4.4"
    name: "Google DNS"
  
  quad9:
    primary: "9.9.9.9"
    secondary: "149.112.112.112"
    name: "Quad9"

output:
  format: "table"
  colors: true
  show_details: false

rate_limiting:
  delay_between_queries: 0.1
  max_concurrent: 10
  backoff_strategy: "exponential"
```

### Environment Variables

You can also configure the tool using environment variables:

```bash
export DNS_BENCHMARK_QUERIES=50
export DNS_BENCHMARK_TIMEOUT=5
export DNS_BENCHMARK_THREADS=8
export DNS_BENCHMARK_CONFIG_PATH=/path/to/config.yaml
```

### Command Line Options

```
Usage: dns-benchmark [OPTIONS]

Options:
  -q, --queries INTEGER        Number of queries per provider [default: 25]
  -t, --timeout FLOAT          Query timeout in seconds [default: 3.0]
  --threads INTEGER            Number of parallel threads [default: 5]
  --domains TEXT               Comma-separated list of test domains
  --providers TEXT             Comma-separated list of DNS provider IPs
  --config PATH                Path to configuration file
  --output PATH                Output file path
  --format [json|csv|table]    Output format [default: table]
  --ipv6                       Use IPv6 DNS servers
  --verbose                    Enable verbose output
  --monitor                    Enable continuous monitoring mode
  --interval INTEGER           Monitoring interval in seconds [default: 60]
  --no-colors                  Disable colored output
  --help                       Show this message and exit
```

## DNS Providers

### Default Provider List

The tool comes pre-configured with a curated list of reliable DNS providers:

| Provider | Primary IP | Secondary IP | Location | Privacy | Notes |
|----------|------------|--------------|----------|---------|-------|
| Cloudflare | 1.1.1.1 | 1.0.0.1 | Global | High | Fastest overall, no logging |
| Google | 8.8.8.8 | 8.8.4.4 | Global | Medium | Reliable, some logging |
| Quad9 | 9.9.9.9 | 149.112.112.112 | Global | High | Security-focused, blocks malware |
| OpenDNS | 208.67.222.222 | 208.67.220.220 | Global | Medium | Family-friendly options |
| AdGuard | 94.140.14.14 | 94.140.15.15 | Global | High | Ad-blocking by default |
| CleanBrowsing | 185.228.168.9 | 185.228.169.9 | Global | High | Content filtering |

### Provider Selection Rationale

The providers are selected based on:

1. **Performance**: Proven low latency and high reliability
2. **Geographic Distribution**: Global anycast networks for consistent performance
3. **Privacy**: Various privacy policies from no-logging to minimal logging
4. **Features**: Additional capabilities like malware blocking, ad filtering
5. **Stability**: Long-standing services with good uptime records

### Adding Custom Providers

You can add custom DNS providers in your configuration file:

```yaml
providers:
  my_custom_provider:
    primary: "192.168.1.1"
    secondary: "192.168.1.2"
    name: "My Local DNS"
    location: "Local Network"
    privacy: "Full Control"
```

### Updating Provider IPs

DNS provider IPs occasionally change. To update them:

1. **Manual Update**: Edit your configuration file with new IPs
2. **Auto-Update**: Run the built-in update command
   ```bash
   dns-benchmark --update-providers
   ```
3. **Verify Changes**: Test updated providers before relying on them

## Metrics Explained

### Latency

**What it measures**: The time it takes for a DNS query to travel from your device to the DNS server and back.

**How it's calculated**: Average round-trip time across all successful queries, measured in milliseconds.

**What's good**: 
- Excellent: < 15ms
- Good: 15-30ms
- Acceptable: 30-50ms
- Poor: > 50ms

**Why it matters**: Lower latency means faster website loading, better gaming performance, and more responsive internet experience.

### Success Rate

**What it measures**: The percentage of DNS queries that receive a valid response.

**How it's calculated**: `(Successful Queries / Total Queries) × 100%`

**What's good**:
- Excellent: 99.5%+
- Good: 98-99.5%
- Acceptable: 95-98%
- Poor: < 95%

**Why it matters**: Higher success rate means more reliable internet access with fewer failed connections.

### Stability Score

**What it measures**: Consistency of performance over time, combining latency variance and success rate consistency.

**How it's calculated**: Complex algorithm considering:
- Standard deviation of latency
- Success rate variance across test runs
- Response time consistency

**What's good**:
- Excellent: 95%+
- Good: 90-95%
- Acceptable: 85-90%
- Poor: < 85%

**Why it matters**: High stability means predictable performance, which is crucial for applications requiring consistent response times.

### Overall Score

**What it measures**: Combined performance metric across all three categories.

**How it's calculated**: Weighted average:
- Latency: 40%
- Success Rate: 35%
- Stability: 25%

**Interpreting Results**:
- **Best Overall**: Highest combined score
- **Fastest**: Lowest average latency
- **Most Reliable**: Highest success rate
- **Most Stable**: Highest stability score

## Advanced Usage

### Custom Test Scenarios

#### Gaming Optimization
```bash
# Test with gaming-focused domains for low latency
dns-benchmark --domains "steamcommunity.com,battle.net,epicgames.com" --queries 50
```

#### Streaming Performance
```bash
# Test with streaming service domains
dns-benchmark --domains "netflix.com,youtube.com,twitch.tv" --timeout 5
```

#### Business/Enterprise
```bash
# Test with business-focused domains
dns-benchmark --domains "office365.com,salesforce.com,slack.com" --threads 10
```

### Automation and Scripting

#### Bash Script Integration
```bash
#!/bin/bash
# Run daily DNS benchmark and log results
RESULTS_FILE="/var/log/dns-benchmark-$(date +%Y%m%d).log"
dns-benchmark --format json --output "$RESULTS_FILE"

# Alert if performance degrades
if ! grep -q '"overall_score": 9[0-9]' "$RESULTS_FILE"; then
    echo "DNS performance degradation detected!" | mail -s "DNS Benchmark Alert" admin@example.com
fi
```

#### Python Integration
```python
import subprocess
import json

# Run benchmark and parse results
result = subprocess.run(['dns-benchmark', '--format', 'json'], capture_output=True, text=True)
data = json.loads(result.stdout)

# Find best provider
best_provider = max(data['providers'], key=lambda x: x['overall_score'])
print(f"Best provider: {best_provider['name']} (Score: {best_provider['overall_score']}%)")
```

### Performance Optimization

#### System-Level Tuning
```bash
# Increase DNS cache size on Linux
echo 'options timeout:1 attempts:3 rotate' | sudo tee /etc/resolv.conf

# Configure systemd-resolved for better performance
sudo systemctl edit systemd-resolved
# Add:
# [Resolve]
# DNS=1.1.1.1 8.8.8.8
# Cache=yes
# DNSStubListener=no
```

#### Network Optimization
```bash
# Use local DNS caching with dnsmasq
sudo apt install dnsmasq
# Configure /etc/dnsmasq.conf with upstream servers
sudo systemctl restart dnsmasq
```

## Troubleshooting

### Common Issues

#### High Latency Results

**Symptoms**: All providers showing > 100ms latency

**Solutions**:
1. Check network connectivity:
   ```bash
   ping -c 4 8.8.8.8
   ping -c 4 1.1.1.1
   ```

2. Test with different domains:
   ```bash
   dns-benchmark --domains "google.com,cloudflare.com"
   ```

3. Check for network congestion:
   ```bash
   # Monitor network usage
   iftop
   nethogs
   ```

4. Try different test times (avoid peak hours)

#### Low Success Rates

**Symptoms**: Success rate below 95% for multiple providers

**Solutions**:
1. Increase timeout value:
   ```bash
   dns-benchmark --timeout 10
   ```

2. Check firewall settings:
   ```bash
   # Ensure port 53 is open
   sudo ufw status
   sudo iptables -L | grep 53
   ```

3. Test with fewer concurrent queries:
   ```bash
   dns-benchmark --threads 2
   ```

4. Check DNS over TLS/HTTPS interference:
   ```bash
   # Disable VPN/proxy temporarily
   dns-benchmark --no-proxy
   ```

#### Rate Limiting Issues

**Symptoms**: Sudden drops in success rate, timeout errors

**Solutions**:
1. Increase delay between queries:
   ```bash
   dns-benchmark --delay 0.5
   ```

2. Reduce concurrent queries:
   ```bash
   dns-benchmark --threads 3
   ```

3. Use exponential backoff:
   ```yaml
   # In config file
   rate_limiting:
     backoff_strategy: "exponential"
     max_retries: 3
   ```

4. Rotate providers more frequently:
   ```bash
   dns-benchmark --rotate-providers
   ```

#### IPv6 Connectivity Issues

**Symptoms**: IPv6 tests failing or showing very high latency

**Solutions**:
1. Check IPv6 connectivity:
   ```bash
   ping6 2001:4860:4860::8888
   ```

2. Test without IPv6:
   ```bash
   dns-benchmark --ipv4-only
   ```

3. Configure IPv6 properly:
   ```bash
   # Check IPv6 configuration
   ip -6 addr show
   ```

### Debug Mode

Enable detailed debugging information:

```bash
dns-benchmark --debug --verbose --log-level debug
```

This will show:
- Individual query details
- Network packet traces
- Provider response analysis
- Error stack traces

### Log Files

Check application logs for detailed error information:

```bash
# Linux/macOS
tail -f ~/.dns-benchmark/logs/app.log

# Windows
type %USERPROFILE%\.dns-benchmark\logs\app.log
```

### Getting Help

1. **Check the logs**: Always check the debug output first
2. **Verify configuration**: Ensure your config file is valid YAML
3. **Test connectivity**: Basic network tests can identify many issues
4. **Update the tool**: Ensure you're running the latest version
   ```bash
   pip install --upgrade dns-benchmark
   ```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Code structure and architecture
- Development setup
- Pull request process
- Coding standards
- Testing requirements

### Quick Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/dns-benchmark.git
cd dns-benchmark

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Install in development mode
pip install -e .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes and updates.