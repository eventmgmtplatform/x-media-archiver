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
from xma.application.reporting import (
    ExecutionReport,
    archive_report,
    download_report,
    failure_report,
)
from xma.domain.archive import ArchiveRequest, ArchiveRun
from xma.domain.discovery import DiscoveryBatch, normalize_discovery_target
from xma.domain.download import DownloadRequest, DownloadSummary
from xma.domain.errors import (
    ArchiveUnexpectedError,
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
    """Interactively download up to ten absolute or add up to twenty videos."""
    database = repository / "catalog.sqlite3"
    telemetry = (
        (lambda message: None)
        if json_output
        else (lambda message: error_console.print(message, markup=False))
    )
    try:
        if limit is not None and add is not None:
            raise DomainError("--limit and --add are mutually exclusive")
        if limit is not None and not 1 <= limit <= 10:
            raise DomainError("download --limit must be between 1 and 10")
        if add is not None and not 1 <= add <= 20:
            raise DomainError("download --add must be between 1 and 20")
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
        if requested_limit > 20:
            raise DomainError("download resulting total must not exceed 20")
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
                telemetry,
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
            telemetry,
            max_scan,
        )
    except (InvalidIdentityError, DomainError) as error:
        _render_failure_report(
            failure_report(
                command="download",
                handle=_safe_handle(target),
                error_code="INVALID_INPUT",
                exit_code=EXIT_INVALID_INPUT,
            ),
            json_output,
            f"invalid input: {error}",
        )
        raise typer.Exit(EXIT_INVALID_INPUT) from error
    except DiscoveryError as error:
        _exit_for_discovery_error(
            error,
            command="download",
            target=target,
            json_output=json_output,
            progress=_download_progress(repository),
        )
    except DownloadError as error:
        _render_failure_report(
            failure_report(
                command="download",
                handle=_safe_handle(target),
                error_code="DOWNLOAD_FAILED",
                exit_code=EXIT_DOWNLOAD_FAILED,
                progress=_download_progress(repository),
            ),
            json_output,
            f"download failed: {error}",
        )
        raise typer.Exit(EXIT_DOWNLOAD_FAILED) from error
    except (CatalogError, IdentityConflictError, sqlite3.Error, OSError) as error:
        _render_failure_report(
            failure_report(
                command="download",
                handle=_safe_handle(target),
                error_code="CATALOG_FAILED",
                exit_code=EXIT_CATALOG_FAILED,
                progress=_download_progress(repository),
            ),
            json_output,
            "download failed: local persistence unavailable or conflicting",
        )
        raise typer.Exit(EXIT_CATALOG_FAILED) from error
    request_mode = "ADD" if add is not None else "LIMIT"
    request_value = add if add is not None else (limit or 1)
    _render_download(
        result,
        json_output,
        download_report(result, mode=request_mode, requested=request_value),
    )


@app.command("archive")
def archive_profile(
    target: Annotated[str, typer.Argument(help="Public X profile target.")],
    limit: Annotated[int | None, typer.Option("--limit", min=1, max=20)] = None,
    all_items: Annotated[
        bool, typer.Option("--all", help="Archive until confirmed provider exhaustion.")
    ] = False,
    resume: Annotated[
        bool, typer.Option("--resume", help="Resume a compatible paused --all run.")
    ] = False,
    max_items: Annotated[
        int | None,
        typer.Option("--max-items", min=1, help="Operational safety cap for --all."),
    ] = None,
    max_runtime: Annotated[int, typer.Option("--max-runtime", min=60, max=21600)] = 3600,
    min_free_space_gib: Annotated[int, typer.Option("--min-free-space-gib", min=5, max=1024)] = 10,
    batch_size: Annotated[int, typer.Option("--batch-size", min=1, max=20)] = 5,
    repository: Annotated[Path, typer.Option("--repository")] = Path("repository"),
    auth_browser: Annotated[str | None, typer.Option("--auth-browser")] = None,
    auth_profile: Annotated[str | None, typer.Option("--auth-profile")] = None,
    request_interval: Annotated[int, typer.Option("--request-interval", min=1, max=60)] = 2,
    discovery_timeout: Annotated[int, typer.Option("--discovery-timeout", min=5, max=60)] = 30,
    quality: Annotated[str, typer.Option("--quality")] = "best",
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Durably archive a bounded total or a complete public profile."""
    database = repository / "catalog.sqlite3"
    telemetry = (
        (lambda message: None)
        if json_output
        else (lambda message: error_console.print(message, markup=False))
    )
    try:
        if all_items and limit is not None:
            raise DomainError("archive --all and --limit are mutually exclusive")
        if max_items is not None and not all_items:
            raise DomainError("archive --max-items requires --all")
        if resume and not all_items:
            raise DomainError("archive --resume requires --all")
        if quality != "best":
            raise DomainError("archive quality must be 'best'")
        request = (
            ArchiveRequest.create_all(
                target,
                batch_size,
                request_interval,
                max_items=max_items,
                max_runtime_seconds=max_runtime,
                min_free_space_gib=min_free_space_gib,
                resume=resume,
            )
            if all_items
            else ArchiveRequest.create(target, limit or 10, batch_size, request_interval)
        )
        provider = _download_incremental_provider(
            auth_browser,
            auth_profile,
            None,
            telemetry,
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
            telemetry,
        )
    except (InvalidIdentityError, DomainError) as error:
        _render_failure_report(
            failure_report(
                command="archive",
                handle=_safe_handle(target),
                error_code="INVALID_INPUT",
                exit_code=EXIT_INVALID_INPUT,
                run=_latest_run(database),
            ),
            json_output,
            f"invalid input: {error}",
        )
        raise typer.Exit(EXIT_INVALID_INPUT) from error
    except DiscoveryError as error:
        _exit_for_discovery_error(
            error,
            command="archive",
            target=target,
            json_output=json_output,
            run=_latest_run(database),
        )
    except DownloadError as error:
        _render_failure_report(
            failure_report(
                command="archive",
                handle=_safe_handle(target),
                error_code="DOWNLOAD_FAILED",
                exit_code=EXIT_DOWNLOAD_FAILED,
                run=_latest_run(database),
            ),
            json_output,
            f"archive failed: {error}",
        )
        raise typer.Exit(EXIT_DOWNLOAD_FAILED) from error
    except ArchiveUnexpectedError as error:
        _render_failure_report(
            failure_report(
                command="archive",
                handle=_safe_handle(target),
                error_code="UNEXPECTED_FAILURE",
                exit_code=EXIT_PROVIDER_FAILED,
                run=_latest_run(database),
            ),
            json_output,
            "archive failed: unexpected internal failure",
        )
        raise typer.Exit(EXIT_PROVIDER_FAILED) from error
    except (CatalogError, IdentityConflictError, sqlite3.Error, OSError) as error:
        _render_failure_report(
            failure_report(
                command="archive",
                handle=_safe_handle(target),
                error_code="CATALOG_FAILED",
                exit_code=EXIT_CATALOG_FAILED,
            ),
            json_output,
            "archive failed: local repository unavailable",
        )
        raise typer.Exit(EXIT_CATALOG_FAILED) from error
    _render_archive(result, json_output, archive_report(result))


@app.command("status")
def archive_status(
    repository: Annotated[Path, typer.Option("--repository")] = Path("repository"),
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Read the latest durable archive checkpoint without network access."""
    result = SQLiteArchiveStore(repository / "catalog.sqlite3").latest()
    if result is None:
        _render_failure_report(
            failure_report(
                command="status",
                handle=None,
                error_code="NOT_FOUND",
                exit_code=EXIT_NOT_FOUND,
            ),
            json_output,
            "archive status unavailable: no durable run",
        )
        raise typer.Exit(EXIT_NOT_FOUND)
    _render_archive(result, json_output, archive_report(result, command="status"))


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


def _exit_for_discovery_error(
    error: Exception,
    *,
    command: str | None = None,
    target: str | None = None,
    json_output: bool = False,
    progress: dict[str, object] | None = None,
    run: ArchiveRun | None = None,
) -> NoReturn:
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
    if command is None:
        error_console.print(f"{label}: {error}", markup=False, style="red")
    else:
        error_code = _discovery_error_code(error)
        _render_failure_report(
            failure_report(
                command=command,
                handle=_safe_handle(target),
                error_code=error_code,
                exit_code=code,
                run=run,
                progress=progress,
            ),
            json_output,
            f"{label}: {error}",
        )
    raise typer.Exit(code) from error


def _discovery_error_code(error: Exception) -> str:
    if isinstance(error, InvalidIdentityError):
        return "INVALID_INPUT"
    if isinstance(error, DiscoveryNotFoundError):
        return "NOT_FOUND"
    if isinstance(error, DiscoveryRestrictedError):
        return "PROVIDER_RESTRICTED"
    if isinstance(error, DiscoveryRateLimitError):
        return "PROVIDER_RATE_LIMITED"
    if isinstance(error, DiscoveryTransientError):
        return "PROVIDER_TRANSIENT"
    return "PROVIDER_FAILED"


def _safe_handle(target: str | None) -> str | None:
    if target is None:
        return None
    try:
        return normalize_discovery_target(target).handle
    except (InvalidIdentityError, DomainError):
        return None


def _download_progress(repository: Path) -> dict[str, object]:
    manifest = repository / "manifests/latest.json"
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    result: dict[str, object] = {}
    for key in (
        "existing_before",
        "downloaded_this_run",
        "skipped_count",
        "failed_count",
        "total_after",
    ):
        value = payload.get(key)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            result[key] = value
    return result


def _latest_run(database: Path) -> ArchiveRun | None:
    try:
        return SQLiteArchiveStore(database).latest()
    except (sqlite3.Error, OSError):
        return None


def _render_failure_report(report: ExecutionReport, json_output: bool, legacy_message: str) -> None:
    if json_output:
        typer.echo(
            json.dumps(report.public_dict(), ensure_ascii=False, sort_keys=True),
            err=True,
        )
        return
    error_console.print(legacy_message, markup=False, style="red")
    _render_execution_report(report, output=error_console)


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


def _render_download(result: DownloadSummary, json_output: bool, report: ExecutionReport) -> None:
    if json_output:
        payload = result.public_dict()
        payload["report"] = report.public_dict()
        typer.echo(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    _render_execution_report(report)


def _render_archive(result: ArchiveRun, json_output: bool, report: ExecutionReport) -> None:
    if json_output:
        payload = result.public_dict()
        payload["report"] = report.public_dict()
        typer.echo(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    _render_execution_report(report)
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
        "mode",
        "completion_reason",
        "failed_total",
        "verified_total",
        "checkpoint",
        "max_items",
        "max_runtime_seconds",
        "min_free_space_bytes",
        "elapsed_seconds",
        "resumable",
        "goal",
        "operational_cap",
    ):
        value = values[key]
        if key == "run_id":
            value = str(value)[:8]
        console.print(f"{key}: {value}", markup=False)


def _render_execution_report(report: ExecutionReport, *, output: Console = console) -> None:
    values = report.public_dict()
    account = values["account"]
    counts = values["counts"]
    checkpoint = values["checkpoint"]
    request = values["request"]
    assert isinstance(account, dict)
    assert isinstance(counts, dict)
    handle = account.get("handle")
    output.print(f"Account: {'@' + str(handle) if handle else 'unavailable'}", markup=False)
    output.print(f"Result: {report.status}", markup=False)
    if isinstance(request, dict):
        requested = request.get("requested")
        label = str(request.get("mode", "")).lower()
        output.print(
            f"Requested: {label}{'' if requested is None else ' ' + str(requested)}",
            markup=False,
        )
    output.print(f"Existing before: {counts.get('existing_before')}", markup=False)
    output.print(f"Downloaded this run: {counts.get('downloaded_this_run')}", markup=False)
    output.print(f"Skipped: {counts.get('skipped')}", markup=False)
    output.print(f"Failed: {counts.get('failed')}", markup=False)
    output.print(f"Total after: {counts.get('total_after')}", markup=False)
    if report.complete is not None:
        output.print(f"Complete: {'yes' if report.complete else 'no'}", markup=False)
    if report.reason is not None:
        output.print(f"Reason: {report.reason}", markup=False)
    if isinstance(checkpoint, dict):
        output.print(f"Checkpoint: {checkpoint.get('page')}", markup=False)
        output.print(f"Remaining: {checkpoint.get('remaining')}", markup=False)
        output.print(f"Resumable: {str(checkpoint.get('resumable')).lower()}", markup=False)
    if report.video is None:
        if report.command == "download" and counts.get("downloaded_this_run") == 0:
            output.print("No new video was downloaded.", markup=False)
        return
    video_report = report.video
    video = video_report.public_dict()
    output.print("\nVideo", markup=False)
    output.print(f"Post: {video['post_id']}", markup=False)
    output.print(f"Media index: {video['media_index']}", markup=False)
    output.print(f"Published: {video['published_at']}", markup=False)
    duration = (
        _duration(video_report.duration_ms) if video_report.duration_ms is not None else "unknown"
    )
    output.print(f"Duration: {duration}", markup=False)
    output.print(f"Resolution: {video['resolution'] or 'unknown'}", markup=False)
    output.print(f"Quality: {video['quality']}", markup=False)
    output.print(f"Format: {str(video['extension']).lstrip('.').upper()}", markup=False)
    output.print(f"Size: {_human_size(video_report.size_bytes)}", markup=False)
    output.print(f"SHA-256: {video['sha256']}", markup=False)
    output.print(f"File: {video['relative_path']}", markup=False)


def _duration(milliseconds: int) -> str:
    seconds = milliseconds // 1000
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def _human_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} KiB"
    return f"{size_bytes / 1024**2:.1f} MiB"
