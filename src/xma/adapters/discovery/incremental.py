"""Terminable worker that streams primitive DTOs over a synchronous pipe."""

import math
import multiprocessing
import sys
import time
from collections.abc import Callable, Iterator, Mapping
from datetime import UTC, date, datetime
from multiprocessing.connection import Connection
from typing import Any

import gallery_dl  # type: ignore[import-untyped]
from gallery_dl import config, exception, job

from xma.adapters.discovery.firefox_auth import (
    BrowserAuthentication,
    CookieFileAuthentication,
    load_cookie_file_x_cookies,
    load_firefox_x_cookies,
)
from xma.adapters.discovery.gallery_dl import (
    GalleryDlExtraction,
    _job_url,
    map_gallery_dl_extraction,
)
from xma.adapters.discovery.gallery_dl import (
    _validate_target_batch as _validate_gallery_target_batch,
)
from xma.domain.discovery import DiscoveryBatch, DiscoveryTarget, DiscoveryTargetKind
from xma.domain.errors import DiscoveryContractError, DiscoveryTransientError

_VIDEO_TYPES = {"video", "animated_gif"}
_IPC_VERSION = 1
_TRANSIENT_TERMINALS = {"PROVIDER_TIMEOUT", "PROVIDER_EXHAUSTED"}
_FAILURE_TERMINALS = {"WORKER_FAILED", "IPC_SERIALIZATION_FAILED"}
_PROFILE_FIELDS = ("id", "name", "nick", "protected")
_POST_FIELDS = (
    "tweet_id",
    "author",
    "num",
    "type",
    "duration",
    "width",
    "height",
    "content",
    "date",
    "retweet_id",
    "quoted_id",
    "reply_id",
)


def _validate_target_batch(target: DiscoveryTarget, batch: DiscoveryBatch) -> None:
    """Apply the shared fail-closed target contract to streamed batches."""
    _validate_gallery_target_batch(target, batch)


def _is_ipc_primitive(value: object) -> bool:
    if value is None or isinstance(value, (str, int, bool)):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, (list, tuple)):
        return all(_is_ipc_primitive(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _is_ipc_primitive(item) for key, item in value.items())
    return False


def _profile_dto(source: Mapping[str, Any]) -> dict[str, Any]:
    user = source.get("user")
    selected = user if isinstance(user, Mapping) else source
    result = {"user": {field: selected.get(field) for field in _PROFILE_FIELDS}}
    if not _is_ipc_primitive(result):
        raise ValueError
    return result


def _candidate_dto(source_url: str, source: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {field: source.get(field) for field in _POST_FIELDS}
    author = source.get("author")
    result["author"] = {"id": author.get("id")} if isinstance(author, Mapping) else author
    if isinstance(result["date"], (datetime, date)):
        result["date"] = result["date"].isoformat()
    result["source_url"] = source_url
    if not _is_ipc_primitive(result):
        raise ValueError
    return result


def _send(connection: Connection, message: dict[str, Any]) -> None:
    if not _is_ipc_primitive(message):
        raise ValueError
    connection.send(message)


def _telemetry(connection: Connection, event: str, **counters: int) -> None:
    _send(connection, {"version": _IPC_VERSION, "kind": "telemetry", "event": event, **counters})


def _terminal(connection: Connection, status: str) -> None:
    _send(connection, {"version": _IPC_VERSION, "kind": "terminal", "status": status})


def _target_dto(target: DiscoveryTarget) -> dict[str, str | None]:
    result = {
        "kind": target.kind.value,
        "canonical_url": target.canonical_url,
        "handle": target.handle,
        "post_id": target.post_id,
    }
    if not _is_ipc_primitive(result):
        raise ValueError
    return result


class _StreamingDataJob(job.DataJob):  # type: ignore[misc]
    def __init__(
        self, url: str, remaining: int, existing: frozenset[str], output: Connection
    ) -> None:
        super().__init__(url, file=None)
        self.remaining, self.existing, self.output = remaining, existing, output
        self.profile_record: dict[str, Any] | None = None
        self.videos_seen = self.duplicates_skipped = self.emitted = 0

    def handle_directory(self, kwdict: dict[str, Any]) -> None:
        if self.profile_record is None:
            self.profile_record = _profile_dto(kwdict)
            _telemetry(self.output, "PROFILE_SEEN")

    def handle_url(self, url: str, kwdict: dict[str, Any]) -> None:
        if str(kwdict.get("type", "")).lower() not in _VIDEO_TYPES:
            return
        self.videos_seen += 1
        _telemetry(self.output, "VIDEO_SEEN", videos_seen=self.videos_seen)
        try:
            identity = f"{kwdict['tweet_id']}:{int(kwdict['num']) - 1}"
        except (KeyError, TypeError, ValueError, OverflowError):
            identity = ""
        if identity and identity in self.existing:
            self.duplicates_skipped += 1
            _telemetry(self.output, "DUPLICATE_SKIPPED", duplicates_skipped=self.duplicates_skipped)
            return
        profile = self.profile_record or _profile_dto(kwdict)
        candidate = _candidate_dto(url, kwdict)
        _send(
            self.output,
            {"version": _IPC_VERSION, "kind": "candidate", "profile": profile, "post": candidate},
        )
        self.emitted += 1
        _telemetry(self.output, "CANDIDATE_SENT", candidates_sent=self.emitted)
        if self.emitted >= self.remaining:
            raise exception.StopExtraction


def _configure_worker(
    authentication: BrowserAuthentication | CookieFileAuthentication | None, request_timeout: int
) -> None:
    if authentication is None:
        cookies = None
    elif isinstance(authentication, BrowserAuthentication):
        cookies = load_firefox_x_cookies(authentication)
    else:
        cookies = load_cookie_file_x_cookies(authentication)
    config.clear()
    for section in (("extractor",), ("extractor", "twitter")):
        config.set(section, "cookies", cookies)
        config.set(section, "cookies-update", False)
    config.set(("extractor",), "username", "")
    config.set(("extractor",), "password", "")
    config.set(("extractor",), "timeout", request_timeout)
    config.set(("extractor", "twitter"), "include", ["timeline"])
    config.set(("extractor", "twitter"), "videos", True)
    config.set(("extractor", "twitter"), "previews", False)
    config.set(("extractor", "twitter"), "retweets", False)
    config.set(("extractor", "twitter"), "quoted", False)
    config.set(("extractor", "twitter"), "text-tweets", False)
    config.set(("extractor",), "download", False)
    config.set(("downloader",), "enabled", False)
    config.set(("cache",), "file", ":memory:")
    config.set(("output",), "private", False)


def _worker_main(
    target: dict[str, str | None],
    remaining: int,
    existing: frozenset[str],
    authentication: BrowserAuthentication | CookieFileAuthentication | None,
    timeout_seconds: int,
    output: Connection,
) -> None:
    terminal = "WORKER_FAILED"
    try:
        _telemetry(output, "WORKER_STARTED")
        _configure_worker(authentication, timeout_seconds)
        _telemetry(output, "AUTH_LOADED")
        job_url = _job_url(
            DiscoveryTarget(
                str(target["handle"]),
                DiscoveryTargetKind(str(target["kind"])),
                str(target["post_id"]) if target["post_id"] is not None else None,
            )
        )
        data_job = _StreamingDataJob(job_url, remaining, existing, output)
        _telemetry(output, "EXTRACTOR_STARTED")
        data_job.run()
        terminal = "COMPLETED" if data_job.emitted else "PROVIDER_EXHAUSTED"
    except exception.StopExtraction:
        terminal = "COMPLETED"
    except (TypeError, ValueError, OverflowError):
        terminal = "IPC_SERIALIZATION_FAILED"
    except BaseException:
        terminal = "WORKER_FAILED"
    try:
        _terminal(output, terminal)
    except (BrokenPipeError, EOFError, OSError, TypeError, ValueError):
        pass
    finally:
        output.close()


def _reconstruct(profile: Mapping[str, Any], post: Mapping[str, Any]) -> GalleryDlExtraction:
    profile_record, post_record = dict(profile), dict(post)
    post_record["_source_url"] = post_record.pop("source_url")
    return GalleryDlExtraction(profile_record, (post_record,))


class IncrementalGalleryDlDiscoveryProvider:
    """Yield candidates while a bounded child process traverses gallery-dl."""

    def __init__(
        self,
        authentication: BrowserAuthentication | CookieFileAuthentication | None = None,
        telemetry: Callable[[str], None] | None = None,
    ) -> None:
        self._authentication = authentication
        self._telemetry = telemetry or (lambda _message: None)

    def candidates(
        self,
        target: DiscoveryTarget,
        remaining: int,
        existing_identities: frozenset[str],
        timeout_seconds: int,
    ) -> Iterator[DiscoveryBatch]:
        if sys.platform != "linux":
            raise DiscoveryTransientError("temporary provider failure [PROVIDER_TIMEOUT]")
        context = multiprocessing.get_context("spawn")
        receiver, sender = context.Pipe(duplex=False)
        process = context.Process(
            target=_worker_main,
            args=(
                _target_dto(target),
                remaining,
                existing_identities,
                self._authentication,
                timeout_seconds,
                sender,
            ),
        )
        process.start()
        sender.close()
        deadline, terminal = time.monotonic() + timeout_seconds, None
        delivered = 0
        try:
            while terminal is None:
                available = deadline - time.monotonic()
                if available <= 0:
                    terminal = (
                        "COMPLETED"
                        if delivered >= remaining
                        else "PROVIDER_TIMEOUT"
                        if process.is_alive()
                        else "WORKER_FAILED"
                    )
                    break
                try:
                    if not receiver.poll(min(available, 0.25)):
                        if not process.is_alive():
                            terminal = "COMPLETED" if delivered >= remaining else "WORKER_FAILED"
                        continue
                    message = receiver.recv()
                except (EOFError, OSError):
                    terminal = "COMPLETED" if delivered >= remaining else "WORKER_FAILED"
                    break
                if not isinstance(message, dict) or not _is_ipc_primitive(message):
                    terminal = "IPC_SERIALIZATION_FAILED"
                    break
                if message.get("version") != _IPC_VERSION:
                    terminal = "WORKER_FAILED"
                    break
                kind = message.get("kind")
                if kind == "telemetry":
                    event = message.get("event")
                    counters = " ".join(
                        f"{key}={value}"
                        for key, value in message.items()
                        if key not in {"version", "kind", "event"}
                    )
                    self._telemetry(f"worker {event}" + (f" {counters}" if counters else ""))
                elif kind == "candidate":
                    batch = map_gallery_dl_extraction(
                        _reconstruct(message["profile"], message["post"]),
                        target,
                        1,
                        datetime.now(UTC),
                        f"gallery-dl:{gallery_dl.__version__}",
                    )
                    _validate_target_batch(target, batch)
                    delivered += batch.asset_count
                    yield batch
                elif kind == "terminal" and message.get("status") in {
                    "COMPLETED",
                    *_TRANSIENT_TERMINALS,
                    *_FAILURE_TERMINALS,
                }:
                    terminal = "COMPLETED" if delivered >= remaining else str(message["status"])
                else:
                    terminal = "WORKER_FAILED"
            if terminal == "COMPLETED":
                return
            if terminal in _TRANSIENT_TERMINALS:
                raise DiscoveryTransientError(f"temporary provider failure [{terminal}]")
            raise DiscoveryContractError(
                f"invalid provider response [{terminal or 'WORKER_FAILED'}]"
            )
        finally:
            receiver.close()
            if process.is_alive():
                process.terminate()
                process.join(1)
            if process.is_alive():
                process.kill()
            process.join()
