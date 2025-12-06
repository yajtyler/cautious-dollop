# Local DNS detection CLI

This repository provides a small cross-platform utility that tries to discover
local DNS resolvers for benchmarking or diagnostic workflows. It currently
supports:

- Parsing `/etc/resolv.conf` and NetworkManager connection profiles on
  Unix-like hosts.
- Reading the output of `scutil --dns` on macOS.
- Reading the output of `ipconfig /all` on Windows.
- Graceful fallbacks to the operating system's resolver APIs
  (`socket.getaddrinfo`) and manual overrides supplied via CLI flags or a
  configuration file.

## Usage

```
python -m local_dns.cli --summary
```

### Manual overrides

```
python -m local_dns.cli --resolver 1.1.1.1 --resolver 9.9.9.9
```

You can also load overrides from a JSON config file that contains a
`"resolvers"` array:

```
python -m local_dns.cli --config resolvers.json
```

## Development

- Dependencies are managed via the standard library.
- Tests are written with `pytest` and live under the `tests/` directory.
