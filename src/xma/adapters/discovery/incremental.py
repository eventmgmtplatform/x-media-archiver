"""Terminable Linux worker that streams gallery-dl candidates to the parent."""

import multiprocessing
import queue
import sys
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import gallery_dl  # type: ignore[import-untyped]
from gallery_dl import config, exception, job

from xma.adapters.discovery.firefox_auth import (
    BrowserAuthentication,
    CookieFileAuthentication,
    load_cookie_file_x_cookies,
    load_firefox_x_cookies,
)
from xma.adapters.discovery.gallery_dl import GalleryDlExtraction, map_gallery_dl_extraction
from xma.domain.discovery import DiscoveryBatch, DiscoveryTarget
from xma.domain.errors import DiscoveryTransientError

_VIDEO_TYPES = {"video", "animated_gif"}


class _StreamingDataJob(job.DataJob):  # type: ignore[misc]
    def __init__(
        self,
        url: str,
        remaining: int,
        existing: frozenset[str],
        output: Any,
    ) -> None:
        super().__init__(url, file=None)
        self.remaining = remaining
        self.existing = existing
        self.output = output
        self.profile_record: dict[str, Any] | None = None
        self.emitted = 0

    def handle_directory(self, kwdict: dict[str, Any]) -> None:
        if self.profile_record is None:
            self.profile_record = dict(kwdict)

    def handle_url(self, url: str, kwdict: dict[str, Any]) -> None:
        if str(kwdict.get("type", "")).lower() not in _VIDEO_TYPES:
            return
        try:
            identity = f"{kwdict['tweet_id']}:{int(kwdict['num']) - 1}"
        except (KeyError, TypeError, ValueError, OverflowError):
            identity = ""
        if identity and identity in self.existing:
            return
        record = dict(kwdict)
        record["_source_url"] = url
        profile = self.profile_record or record
        self.output.put(("candidate", profile, record))
        self.emitted += 1
        if self.emitted >= self.remaining:
            raise exception.StopExtraction


def _configure_worker(
    authentication: BrowserAuthentication | CookieFileAuthentication | None,
    request_timeout: int,
) -> None:
    if authentication is None:
        cookies = None
    elif isinstance(authentication, BrowserAuthentication):
        cookies = load_firefox_x_cookies(authentication)
    else:
        cookies = load_cookie_file_x_cookies(authentication)
    config.clear()
    config.set(("extractor",), "cookies", cookies)
    config.set(("extractor",), "cookies-update", False)
    config.set(("extractor",), "username", "")
    config.set(("extractor",), "password", "")
    config.set(("extractor",), "timeout", request_timeout)
    config.set(("extractor", "twitter"), "cookies", cookies)
    config.set(("extractor", "twitter"), "cookies-update", False)
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
    url: str,
    remaining: int,
    existing: frozenset[str],
    authentication: BrowserAuthentication | CookieFileAuthentication | None,
    timeout_seconds: int,
    output: Any,
) -> None:
    try:
        _configure_worker(authentication, timeout_seconds)
        data_job = _StreamingDataJob(
            url.rstrip("/") + "/timeline",
            remaining,
            existing,
            output,
        )
        data_job.run()
        output.put(("done", data_job.emitted))
    except BaseException:
        output.put(("failed",))


class IncrementalGalleryDlDiscoveryProvider:
    """Yield candidates while a bounded child process traverses gallery-dl."""

    def __init__(
        self,
        authentication: BrowserAuthentication | CookieFileAuthentication | None = None,
    ) -> None:
        self._authentication = authentication

    def candidates(
        self,
        target: DiscoveryTarget,
        remaining: int,
        existing_identities: frozenset[str],
        timeout_seconds: int,
    ) -> Iterator[DiscoveryBatch]:
        if sys.platform != "linux":
            raise DiscoveryTransientError("temporary provider failure [PROVIDER_TIMEOUT]")
        context = multiprocessing.get_context("fork")
        output = context.Queue()
        process = context.Process(
            target=_worker_main,
            args=(
                target.canonical_url,
                remaining,
                existing_identities,
                self._authentication,
                timeout_seconds,
                output,
            ),
        )
        process.start()
        deadline = time.monotonic() + timeout_seconds
        completed = False
        try:
            while True:
                available = deadline - time.monotonic()
                if available <= 0:
                    raise DiscoveryTransientError("temporary provider failure [PROVIDER_TIMEOUT]")
                try:
                    event = output.get(timeout=min(available, 0.25))
                except queue.Empty:
                    if not process.is_alive():
                        break
                    continue
                kind = event[0]
                if kind == "candidate":
                    batch = map_gallery_dl_extraction(
                        GalleryDlExtraction(event[1], (event[2],)),
                        target,
                        1,
                        datetime.now(UTC),
                        f"gallery-dl:{gallery_dl.__version__}",
                    )
                    yield batch
                elif kind == "done":
                    completed = True
                    break
                else:
                    break
            if not completed:
                raise DiscoveryTransientError("temporary provider failure [PROVIDER_EXHAUSTED]")
        finally:
            if process.is_alive():
                process.terminate()
                process.join(1)
            if process.is_alive():
                process.kill()
            process.join()
            output.close()
            output.join_thread()
