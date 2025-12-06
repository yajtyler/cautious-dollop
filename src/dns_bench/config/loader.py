"""Configuration loader for DNS Benchmark."""

import json
from pathlib import Path

import yaml

from dns_bench.config.models import Config


class ConfigLoader:
    """Load configuration from YAML or JSON files."""

    def load(self, config_path: str) -> Config:
        """
        Load configuration from file.

        Args:
            config_path: Path to config file (YAML or JSON)

        Returns:
            Parsed Config object

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config format is invalid
        """
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(path, "r") as f:
            if config_path.endswith(".yaml") or config_path.endswith(".yml"):
                data = yaml.safe_load(f)
            elif config_path.endswith(".json"):
                data = json.load(f)
            else:
                raise ValueError(
                    f"Unsupported config format. Use .yaml, .yml, or .json"
                )

        if data is None:
            data = {}

        return Config(**data)
