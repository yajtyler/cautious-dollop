"""CLI entry point for DNS Benchmark tool."""

import click
from pathlib import Path
from rich.console import Console

from dns_bench import __version__
from dns_bench.config.loader import ConfigLoader
from dns_bench.core.di import ServiceContainer

console = Console()


@click.group()
@click.version_option(
    version=__version__,
    prog_name="dns-bench",
    message="%(prog)s, version %(version)s",
)
@click.option(
    "--config",
    "-c",
    default="config/config.yaml",
    type=click.Path(exists=False),
    help="Path to configuration file",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.pass_context
def app(ctx: click.Context, config: str, verbose: bool) -> None:
    """DNS Benchmark Tool - Benchmark and analyze DNS resolver performance."""
    ctx.ensure_object(dict)

    try:
        config_path = Path(config)
        if config_path.exists():
            config_loader = ConfigLoader()
            loaded_config = config_loader.load(str(config_path))

            container = ServiceContainer(loaded_config)
            ctx.obj["container"] = container
            ctx.obj["config"] = loaded_config
            ctx.obj["verbose"] = verbose

            if verbose:
                console.print("[bold cyan]DNS Benchmark initialized[/bold cyan]")
                console.print(f"Config: {config}")
        elif verbose:
            console.print(
                f"[yellow]Warning: Configuration file not found: {config}[/yellow]"
            )
            ctx.obj["verbose"] = verbose
        else:
            ctx.obj["verbose"] = verbose
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Exit(code=1)


@app.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    """Display version information."""
    console.print(f"DNS Benchmark v{__version__}")


if __name__ == "__main__":
    app()
