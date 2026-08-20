"""Dependency injection container for DNS Benchmark."""

from typing import Any, Optional

from dns_bench.config.models import Config


class ServiceContainer:
    """
    Service container for dependency injection.

    Manages dependencies and their lifecycle throughout the application.
    """

    def __init__(self, config: Config) -> None:
        """
        Initialize service container with configuration.

        Args:
            config: DNS Benchmark configuration
        """
        self.config = config
        self._services: dict[str, Any] = {}
        self._singletons: dict[str, Any] = {}

    def register(self, name: str, service: Any, singleton: bool = False) -> None:
        """
        Register a service in the container.

        Args:
            name: Service identifier
            service: Service instance or factory function
            singleton: Whether to cache the service instance
        """
        self._services[name] = service
        if singleton:
            self._singletons[name] = None

    def get(self, name: str) -> Any:
        """
        Get a service from the container.

        Args:
            name: Service identifier

        Returns:
            Service instance

        Raises:
            KeyError: If service not registered
        """
        service_factory = self._services.get(name)
        if service_factory is None and name not in self._services:
            raise KeyError(f"Service '{name}' not registered in container")

        if name in self._singletons:
            singleton_instance = self._singletons[name]
            if singleton_instance is None:
                singleton_instance = (
                    service_factory() if callable(service_factory) else service_factory
                )
                self._singletons[name] = singleton_instance
            return singleton_instance

        return service_factory() if callable(service_factory) else service_factory

    def has(self, name: str) -> bool:
        """
        Check if service is registered.

        Args:
            name: Service identifier

        Returns:
            True if service is registered
        """
        return name in self._services

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._singletons.clear()
