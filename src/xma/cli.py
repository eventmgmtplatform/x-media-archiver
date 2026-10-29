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
from xma.adapters.archive import RepositoryArchiveLock, SQLiteArchiveStore
from xma.adapters.catalog.sqlite import SQLiteUnitOfWork
from xma.adapters.discovery import (
    BoundedDiscoveryProvider,
    BrowserAuthentication,
    CookieFileAuthentication,
    GalleryDlDiscoveryProvider,
    IncrementalGalleryDlDiscoveryProvider,
)
from xma.adapters.download import HttpMediaDownloadProvider
from xma.application.archive import ArchiveService
from xma.application.discovery import DiscoveryService, SyncResult
from xma.application.download import DownloadService
from xma.domain.archive import ArchiveRequest, ArchiveRun
from xma.domain.discovery import DiscoveryBatch, normalize_discovery_target
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
        int | None,
        typer.Option("--limit", help="Desired verified total, from 1 to 10."),
    ] = None,
    add: Annotated[
        int | None,
        typer.Option(
            "--add",
            help="New videos to add, from 1 to 10; repository total cannot exceed 10.",
        ),
    ] = None,
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
    discovery_attempts: Annotated[
        int,
        typer.Option(
            "--discovery-attempts",
            min=1,
            max=2,
            help="Bounded discovery worker attempts.",
        ),
    ] = 2,
    max_scan: Annotated[
        int,
        typer.Option("--max-scan", min=1, max=500, help="Maximum observed candidates per worker."),
    ] = 100,
    quality: Annotated[
        str,
        typer.Option("--quality", help="Provider quality policy (best only)."),
    ] = "best",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Emit stable JSON without credentials or media URLs."),
    ] = False,
) -> None:
    """Interactively download a bounded total of at most ten public videos."""
    database = repository / "catalog.sqlite3"
    try:
        if limit is not None and add is not None:
            raise DomainError("--limit and --add are mutually exclusive")
        for value in (limit, add):
            if value is not None and not 1 <= value <= 10:
                raise DomainError(
                    "download supports totals from 1 to 10; larger operations require "
                    "the durable 'xma archive' workflow. v0.1.1 does not execute totals above 10"
                )
        if quality != "best":
            raise DomainError("download quality must be 'best'")
        normalized = normalize_discovery_target(target)
        preflight = DownloadService(
            None,
            None,
            lambda: _catalog_unit(database),
            repository,
        )
        existing = preflight.verified_total(normalized.handle)
        requested_limit = (existing + add) if add is not None else (limit or 1)
        if requested_limit > 10:
            raise DomainError(
                "download supports totals from 1 to 10; larger operations require "
                "the durable 'xma archive' workflow. v0.1.1 does not execute totals above 10"
            )
        request = DownloadRequest(target, requested_limit)
        if existing >= requested_limit:
            service = preflight
            incremental_provider = None
        else:
            provider = _download_discovery_provider(
                auth_browser, auth_profile, cookies_file, discovery_timeout
            )
            incremental_provider = _download_incremental_provider(
                auth_browser,
                auth_profile,
                cookies_file,
                lambda message: error_console.print(message, markup=False),
            )
            service = DownloadService(
                provider,
                _media_provider_factory(),
                lambda: _catalog_unit(database),
                repository,
            )
        result = service.execute_incremental(
            request,
            incremental_provider,
            discovery_timeout,
            discovery_attempts,
            lambda message: error_console.print(message, markup=False),
            max_scan,
        )
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


@app.command("archive")
def archive_profile(
    target: Annotated[str, typer.Argument(help="Public X profile target.")],
    limit: Annotated[int, typer.Option("--limit", min=1, max=10)] = 10,
    batch_size: Annotated[int, typer.Option("--batch-size", min=1, max=5)] = 2,
    repository: Annotated[Path, typer.Option("--repository")] = Path("repository"),
    auth_browser: Annotated[str | None, typer.Option("--auth-browser")] = None,
    auth_profile: Annotated[str | None, typer.Option("--auth-profile")] = None,
    request_interval: Annotated[int, typer.Option("--request-interval", min=1, max=60)] = 2,
    discovery_timeout: Annotated[int, typer.Option("--discovery-timeout", min=5, max=60)] = 30,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Durably archive a public profile with checkpoints, currently up to ten."""
    database = repository / "catalog.sqlite3"
    try:
        request = ArchiveRequest.create(target, limit, batch_size, request_interval)
        provider = _download_incremental_provider(
            auth_browser,
            auth_profile,
            None,
            lambda message: error_console.print(message, markup=False),
        )
        download = DownloadService(
            _provider_factory(),
            _media_provider_factory(),
            lambda: _catalog_unit(database),
            repository,
        )
        result = ArchiveService(
            download,
            provider,
            SQLiteArchiveStore(database),
            RepositoryArchiveLock(repository),
        ).execute(
            request,
            discovery_timeout,
            lambda message: error_console.print(message, markup=False),
        )
    except (InvalidIdentityError, DomainError) as error:
        error_console.print(f"invalid input: {error}", markup=False, style="red")
        raise typer.Exit(EXIT_INVALID_INPUT) from error
    except DiscoveryError as error:
        _exit_for_discovery_error(error)
    except DownloadError as error:
        error_console.print(f"archive failed: {error}", markup=False, style="red")
        raise typer.Exit(EXIT_DOWNLOAD_FAILED) from error
    except (CatalogError, IdentityConflictError, sqlite3.Error, OSError) as error:
        error_console.print("archive failed: local repository unavailable", markup=False)
        raise typer.Exit(EXIT_CATALOG_FAILED) from error
    _render_archive(result, json_output)


@app.command("status")
def archive_status(
    repository: Annotated[Path, typer.Option("--repository")] = Path("repository"),
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Read the latest durable archive checkpoint without network access."""
    result = SQLiteArchiveStore(repository / "catalog.sqlite3").latest()
    if result is None:
        error_console.print("archive status unavailable: no durable run", markup=False)
        raise typer.Exit(EXIT_NOT_FOUND)
    _render_archive(result, json_output)


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
            cookie_authentication = CookieFileAuthentication(cookies_file)
        except ValueError as error:
            raise InvalidIdentityError("cookie file configuration is invalid") from error
        provider: DiscoveryProvider = GalleryDlDiscoveryProvider(
            authentication=cookie_authentication,
            request_timeout=discovery_timeout,
        )
    else:
        if browser is None and profile is None:
            provider = _provider_factory()
        elif browser is None or profile is None:
            raise InvalidIdentityError("browser authentication requires both options")
        else:
            try:
                browser_authentication = BrowserAuthentication(browser, profile)
            except ValueError as error:
                raise InvalidIdentityError(
                    "browser authentication configuration is invalid"
                ) from error
            provider = GalleryDlDiscoveryProvider(
                authentication=browser_authentication,
                request_timeout=discovery_timeout,
            )
    try:
        return BoundedDiscoveryProvider(provider, discovery_timeout)
    except ValueError as error:
        raise InvalidIdentityError("discovery timeout must be between 5 and 60 seconds") from error


def _download_incremental_provider(
    browser: str | None,
    profile: str | None,
    cookies_file: Path | None,
    telemetry: Callable[[str], None] | None = None,
) -> IncrementalGalleryDlDiscoveryProvider:
    authentication = _validate_download_authentication(browser, profile, cookies_file)
    return IncrementalGalleryDlDiscoveryProvider(authentication, telemetry)


def _validate_download_authentication(
    browser: str | None,
    profile: str | None,
    cookies_file: Path | None,
) -> BrowserAuthentication | CookieFileAuthentication | None:
    if cookies_file is not None and (browser is not None or profile is not None):
        raise InvalidIdentityError("download authentication options are mutually exclusive")
    if cookies_file is not None:
        try:
            authentication: BrowserAuthentication | CookieFileAuthentication | None = (
                CookieFileAuthentication(cookies_file)
            )
        except ValueError as error:
            raise InvalidIdentityError("cookie file configuration is invalid") from error
    elif browser is None and profile is None:
        authentication = None
    elif browser is None or profile is None:
        raise InvalidIdentityError("browser authentication requires both options")
    else:
        try:
            authentication = BrowserAuthentication(browser, profile)
        except ValueError as error:
            raise InvalidIdentityError("browser authentication configuration is invalid") from error
    return authentication


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


def _render_archive(result: ArchiveRun, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps(result.public_dict(), ensure_ascii=False, sort_keys=True))
        return
    values = result.public_dict()
    for key in (
        "run_id",
        "target",
        "status",
        "requested_total",
        "existing_before",
        "downloaded_total",
        "remaining",
        "page_number",
        "checkpoint_strategy",
        "last_error_code",
        "updated_at",
        "complete",
    ):
        value = values[key]
        if key == "run_id":
            value = str(value)[:8]
        console.print(f"{key}: {value}", markup=False)
