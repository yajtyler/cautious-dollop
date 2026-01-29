"""CLI entry point for DNS Benchmark tool."""

from pathlib import Path

import click
from rich.console import Console

from dns_bench import __version__
from dns_bench.benchmark import run_benchmark
from dns_bench.config.loader import ConfigLoader
from dns_bench.core.di import ServiceContainer
from dns_bench.results import display_results

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
    ctx_obj = ctx.obj  # type: ignore

    try:
        config_path = Path(config)
        if config_path.exists():
            config_loader = ConfigLoader()
            loaded_config = config_loader.load(str(config_path))

            container = ServiceContainer(loaded_config)
            ctx_obj["container"] = container
            ctx_obj["config"] = loaded_config
            ctx_obj["verbose"] = verbose

            if verbose:
                console.print("[bold cyan]DNS Benchmark initialized[/bold cyan]")
                console.print(f"Config: {config}")
        elif verbose:
            console.print(f"[yellow]Warning: Configuration file not found: {config}[/yellow]")
            ctx_obj["verbose"] = verbose
        else:
            ctx_obj["verbose"] = verbose
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Exit(code=1)  # type: ignore


@app.command()
@click.pass_context
def version(ctx: click.Context) -> None:
    """Display version information."""
    console.print(f"DNS Benchmark v{__version__}")


@app.command()
@click.option(
    "--providers",
    "-p",
    multiple=True,
    required=False,
    help="DNS provider IP addresses",
)
@click.option(
    "--domains",
    "-d",
    multiple=True,
    required=False,
    help="Domain names to benchmark",
)
@click.option(
    "--iterations",
    "-i",
    type=int,
    default=1,
    help="Number of iterations per provider+domain",
)
@click.option(
    "--timeout",
    "-t",
    type=float,
    default=5.0,
    help="Query timeout in seconds",
)
@click.pass_context
def run(
    ctx: click.Context,
    providers: tuple,
    domains: tuple,
    iterations: int,
    timeout: float,
) -> None:
    """Run DNS benchmarks."""
    ctx_obj = ctx.obj or {}
    verbose = ctx_obj.get("verbose", False)

    providers_list = list(providers)
    domains_list = list(domains)

    if not providers_list or not domains_list:
        config = ctx_obj.get("config")
        if config:
            providers_list = [p.primary_ip for p in config.providers] or providers_list
            domains_list = [d.name for d in config.domains] or domains_list
        else:
            console.print("[bold red]Error:[/bold red] No providers or domains specified")
            raise click.Exit(code=1)  # type: ignore

    if verbose:
        console.print(
            f"[cyan]Running benchmark with {len(providers_list)} provider(s) "
            f"and {len(domains_list)} domain(s), {iterations} iteration(s) each[/cyan]"
        )

    try:
        results = run_benchmark(
            providers=providers_list,
            domains=domains_list,
            timeout=timeout,
            iterations=iterations,
        )

        if results:
            display_results(results, console=console)

            if verbose:
                console.print()
                console.print(f"[green]Completed {len(results)} total queries[/green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if verbose:
            import traceback

            traceback.print_exc()
        raise click.Exit(code=1)  # type: ignore


if __name__ == "__main__":
    app()
