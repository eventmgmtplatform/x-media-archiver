"""Command-line entry point."""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from rich.console import Console
from rich.table import Table

from xma import __version__
from xma.adapters.catalog.sqlite import SQLiteUnitOfWork
from xma.adapters.discovery import GalleryDlDiscoveryProvider
from xma.application.discovery import DiscoveryService, SyncResult
from xma.domain.discovery import DiscoveryBatch
from xma.domain.errors import (
    DiscoveryError,
    DiscoveryRateLimitError,
    DiscoveryRestrictedError,
    InvalidIdentityError,
)
from xma.domain.ports import DiscoveryProvider

app = typer.Typer(
    name="xma",
    help="Catalog and archive public audiovisual content from X.",
    no_args_is_help=False,
    invoke_without_command=True,
    add_completion=False,
)
console = Console()
error_console = Console(stderr=True)
_provider_factory: Callable[[], DiscoveryProvider] = GalleryDlDiscoveryProvider

EXIT_INVALID_INPUT = 2
EXIT_RESTRICTED = 3
EXIT_RATE_LIMITED = 4
EXIT_PROVIDER_FAILED = 5


@app.callback()
def main(ctx: typer.Context) -> None:
    """X Media Archiver command group."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help(), markup=False)


@app.command()
def version(
    short: Annotated[
        bool,
        typer.Option("--short", help="Print only the semantic version."),
    ] = False,
) -> None:
    """Display version information."""
    value = __version__ if short else f"X Media Archiver {__version__}"
    console.print(value, markup=False)


@app.command("inspect")
def inspect_profile(
    target: Annotated[str, typer.Argument(help="Public @handle or X profile URL.")],
    limit: Annotated[
        int,
        typer.Option("--limit", min=1, max=100, help="Maximum video assets to inspect."),
    ] = 10,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Emit stable JSON without signed media URLs."),
    ] = False,
) -> None:
    """Inspect public video metadata without writing a catalog or media."""
    try:
        batch = DiscoveryService(_provider_factory()).inspect(target, limit)
    except (InvalidIdentityError, DiscoveryError) as error:
        _exit_for_discovery_error(error)
    _render_batch(batch, json_output)


@app.command("sync")
def sync_profile(
    target: Annotated[str, typer.Argument(help="Public @handle or X profile URL.")],
    limit: Annotated[
        int,
        typer.Option("--limit", min=1, max=100, help="Maximum video assets to catalog."),
    ] = 10,
    repository: Annotated[
        Path,
        typer.Option("--repository", help="Local XMA repository directory."),
    ] = Path("repository"),
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show discovery without persisting SQLite."),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Emit stable JSON without signed media URLs."),
    ] = False,
) -> None:
    """Synchronize public video metadata into the local SQLite catalog."""
    if not dry_run:
        repository.mkdir(parents=True, exist_ok=True)
    database = repository / "catalog.sqlite3"
    service = DiscoveryService(
        _provider_factory(),
        None if dry_run else lambda: SQLiteUnitOfWork(database),
    )
    try:
        result = service.sync(target, limit, dry_run=dry_run)
    except (InvalidIdentityError, DiscoveryError) as error:
        _exit_for_discovery_error(error)
    _render_sync(result, json_output, database)


def _exit_for_discovery_error(error: Exception) -> NoReturn:
    if isinstance(error, InvalidIdentityError):
        code = EXIT_INVALID_INPUT
    elif isinstance(error, DiscoveryRestrictedError):
        code = EXIT_RESTRICTED
    elif isinstance(error, DiscoveryRateLimitError):
        code = EXIT_RATE_LIMITED
    else:
        code = EXIT_PROVIDER_FAILED
    label = "invalid input" if isinstance(error, InvalidIdentityError) else "discovery failed"
    error_console.print(f"{label}: {error}", markup=False, style="red")
    raise typer.Exit(code) from error


def _render_batch(batch: DiscoveryBatch, json_output: bool) -> None:
    if json_output:
        console.print(json.dumps(batch.public_dict(), ensure_ascii=False, sort_keys=True))
        return
    table = Table(title=f"@{batch.profile.handle} public videos")
    table.add_column("Post")
    table.add_column("Published (UTC)")
    table.add_column("Type")
    table.add_column("Size")
    for post in batch.posts:
        for asset in post.assets:
            size = "?" if asset.width is None else f"{asset.width}x{asset.height or '?'}"
            table.add_row(post.post_id, post.published_at.isoformat(), asset.media_type.value, size)
    console.print(table)
    console.print(
        f"Observed {batch.asset_count} video asset(s) from {batch.provider}; "
        f"limit={batch.requested_limit}. Coverage is observational, not complete.",
        markup=False,
    )
    for warning in batch.warnings:
        console.print(f"warning: {warning}", markup=False, style="yellow")


def _render_sync(result: SyncResult, json_output: bool, database: Path) -> None:
    if json_output:
        console.print(json.dumps(result.public_dict(), ensure_ascii=False, sort_keys=True))
        return
    _render_batch(result.batch, False)
    if result.dry_run:
        console.print("Dry run: no catalog was written.", markup=False)
    else:
        console.print(f"Catalog: {database}", markup=False)
        console.print(f"Discovery run: {result.run_id}", markup=False)
