"""Command-line entry point."""

import json
import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, NoReturn

import typer
from rich.console import Console
from rich.table import Table

from xma import __version__
from xma.adapters.catalog.sqlite import SQLiteUnitOfWork
from xma.adapters.discovery import (
    BoundedDiscoveryProvider,
    BrowserAuthentication,
    CookieFileAuthentication,
    GalleryDlDiscoveryProvider,
)
from xma.adapters.download import HttpMediaDownloadProvider
from xma.application.discovery import DiscoveryService, SyncResult
from xma.application.download import DownloadService
from xma.domain.discovery import DiscoveryBatch
from xma.domain.download import DownloadRequest, DownloadSummary
from xma.domain.errors import (
    CatalogError,
    DiscoveryError,
    DiscoveryNotFoundError,
    DiscoveryRateLimitError,
    DiscoveryRestrictedError,
    DiscoveryTransientError,
    DomainError,
    DownloadError,
    IdentityConflictError,
    InvalidIdentityError,
)
from xma.domain.ports import DiscoveryProvider, MediaDownloadProvider

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
_media_provider_factory: Callable[[], MediaDownloadProvider] = HttpMediaDownloadProvider


def _authenticated_provider_factory(authentication: BrowserAuthentication) -> DiscoveryProvider:
    return GalleryDlDiscoveryProvider(authentication=authentication)


EXIT_INVALID_INPUT = 2
EXIT_RESTRICTED = 3
EXIT_RATE_LIMITED = 4
EXIT_PROVIDER_FAILED = 5
EXIT_CATALOG_FAILED = 6
EXIT_NOT_FOUND = 7
EXIT_TRANSIENT = 8
EXIT_DOWNLOAD_FAILED = 9


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
    auth_browser: Annotated[
        str | None,
        typer.Option("--auth-browser", help="Local browser session source (Firefox only)."),
    ] = None,
    auth_profile: Annotated[
        str | None,
        typer.Option("--auth-profile", help="Local Firefox profile name."),
    ] = None,
) -> None:
    """Inspect public video metadata without writing a catalog or media."""
    try:
        provider = _discovery_provider(auth_browser, auth_profile)
        batch = DiscoveryService(provider).inspect(target, limit)
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
    auth_browser: Annotated[
        str | None,
        typer.Option("--auth-browser", help="Local browser session source (Firefox only)."),
    ] = None,
    auth_profile: Annotated[
        str | None,
        typer.Option("--auth-profile", help="Local Firefox profile name."),
    ] = None,
) -> None:
    """Synchronize public video metadata into the local SQLite catalog."""
    database = repository / "catalog.sqlite3"
    try:
        provider = _discovery_provider(auth_browser, auth_profile)
        service = DiscoveryService(
            provider,
            None if dry_run else lambda: _catalog_unit(database),
        )
        result = service.sync(target, limit, dry_run=dry_run)
    except (InvalidIdentityError, DiscoveryError) as error:
        _exit_for_discovery_error(error)
    except (CatalogError, IdentityConflictError, sqlite3.Error, OSError) as error:
        error_console.print(
            "catalog failed: local persistence unavailable or conflicting", markup=False
        )
        raise typer.Exit(EXIT_CATALOG_FAILED) from error
    _render_sync(result, json_output, database)


@app.command("download")
def download_profile(
    target: Annotated[str, typer.Argument(help="Public @handle or X profile URL.")],
    limit: Annotated[
        int,
        typer.Option("--limit", min=1, max=5, help="Video assets to download (maximum 5)."),
    ] = 1,
    repository: Annotated[
        Path,
        typer.Option("--repository", help="Local XMA repository directory."),
    ] = Path("repository"),
    auth_browser: Annotated[
        str | None,
        typer.Option("--auth-browser", help="Local browser session source (Firefox only)."),
    ] = None,
    auth_profile: Annotated[
        str | None,
        typer.Option("--auth-profile", help="Local Firefox profile name."),
    ] = None,
    cookies_file: Annotated[
        Path | None,
        typer.Option("--cookies-file", help="Caller-owned Netscape cookie file."),
    ] = None,
    discovery_timeout: Annotated[
        int,
        typer.Option(
            "--discovery-timeout",
            min=5,
            max=60,
            help="Total discovery deadline in seconds (Linux only).",
        ),
    ] = 30,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Emit stable JSON without credentials or media URLs."),
    ] = False,
) -> None:
    """Download a bounded vertical slice of public video assets."""
    database = repository / "catalog.sqlite3"
    try:
        provider = _download_discovery_provider(
            auth_browser, auth_profile, cookies_file, discovery_timeout
        )
        request = DownloadRequest(target, limit)
        result = DownloadService(
            provider,
            _media_provider_factory(),
            lambda: _catalog_unit(database),
            repository,
        ).execute(request)
    except (InvalidIdentityError, DomainError) as error:
        error_console.print(f"invalid input: {error}", markup=False, style="red")
        raise typer.Exit(EXIT_INVALID_INPUT) from error
    except DiscoveryError as error:
        _exit_for_discovery_error(error)
    except DownloadError as error:
        error_console.print(f"download failed: {error}", markup=False, style="red")
        raise typer.Exit(EXIT_DOWNLOAD_FAILED) from error
    except (CatalogError, IdentityConflictError, sqlite3.Error, OSError) as error:
        error_console.print(
            "download failed: local persistence unavailable or conflicting", markup=False
        )
        raise typer.Exit(EXIT_CATALOG_FAILED) from error
    _render_download(result, json_output)


def _discovery_provider(browser: str | None, profile: str | None) -> DiscoveryProvider:
    if browser is None and profile is None:
        return _provider_factory()
    if browser is None or profile is None:
        raise InvalidIdentityError("browser authentication requires both options")
    try:
        authentication = BrowserAuthentication(browser, profile)
    except ValueError as error:
        raise InvalidIdentityError("browser authentication configuration is invalid") from error
    return _authenticated_provider_factory(authentication)


def _download_discovery_provider(
    browser: str | None,
    profile: str | None,
    cookies_file: Path | None,
    discovery_timeout: int,
) -> DiscoveryProvider:
    if cookies_file is not None and (browser is not None or profile is not None):
        raise InvalidIdentityError("download authentication options are mutually exclusive")
    if cookies_file is not None:
        try:
            authentication = CookieFileAuthentication(cookies_file)
        except ValueError as error:
            raise InvalidIdentityError("cookie file configuration is invalid") from error
        provider: DiscoveryProvider = GalleryDlDiscoveryProvider(authentication=authentication)
    else:
        provider = _discovery_provider(browser, profile)
    try:
        return BoundedDiscoveryProvider(provider, discovery_timeout)
    except ValueError as error:
        raise InvalidIdentityError("discovery timeout must be between 5 and 60 seconds") from error


def _catalog_unit(database: Path) -> SQLiteUnitOfWork:
    database.parent.mkdir(parents=True, exist_ok=True)
    return SQLiteUnitOfWork(database)


def _exit_for_discovery_error(error: Exception) -> NoReturn:
    if isinstance(error, InvalidIdentityError):
        code = EXIT_INVALID_INPUT
    elif isinstance(error, DiscoveryNotFoundError):
        code = EXIT_NOT_FOUND
    elif isinstance(error, DiscoveryTransientError):
        code = EXIT_TRANSIENT
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
        typer.echo(json.dumps(batch.public_dict(), ensure_ascii=False, sort_keys=True))
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
        typer.echo(json.dumps(result.public_dict(), ensure_ascii=False, sort_keys=True))
        return
    _render_batch(result.batch, False)
    if result.dry_run:
        console.print("Dry run: no catalog was written.", markup=False)
    else:
        console.print(f"Catalog: {database}", markup=False)
        console.print(f"Discovery run: {result.run_id}", markup=False)


def _render_download(result: DownloadSummary, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps(result.public_dict(), ensure_ascii=False, sort_keys=True))
        return
    console.print(
        f"Downloaded {result.downloaded_count}; skipped {result.skipped_count}; "
        f"failed {result.failed_count}.",
        markup=False,
    )
