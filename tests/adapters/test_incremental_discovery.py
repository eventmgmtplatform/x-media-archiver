"""Offline worker and IPC tests for incremental gallery-dl discovery."""

import json
import queue
from pathlib import Path
from typing import Any, cast

import pytest
from gallery_dl import config, exception  # type: ignore[import-untyped]

import xma.adapters.discovery.incremental as incremental
from xma.adapters.discovery.firefox_auth import BrowserAuthentication, CookieFileAuthentication
from xma.domain.discovery import normalize_discovery_target
from xma.domain.errors import DiscoveryTransientError

FIXTURE = Path(__file__).parents[1] / "fixtures/gallery_dl/twitter_videos.json"


class CapturingQueue:
    def __init__(self, events: list[tuple[object, ...]] | None = None) -> None:
        self.events = list(events or [])
        self.closed = False

    def put(self, event: tuple[object, ...]) -> None:
        self.events.append(event)

    def get(self, timeout: float) -> tuple[object, ...]:
        del timeout
        if not self.events:
            raise queue.Empty
        return self.events.pop(0)

    def close(self) -> None:
        self.closed = True

    def join_thread(self) -> None:
        return None


def test_streaming_job_skips_existing_and_emits_new_candidate() -> None:
    output = CapturingQueue()
    data_job = incremental._StreamingDataJob(
        "https://x.com/Reuters/timeline", 1, frozenset({"10:0"}), output
    )
    data_job.handle_directory({"user": {"id": "123"}})
    data_job.handle_url("photo", {"type": "photo"})
    data_job.handle_url("old", {"type": "video", "tweet_id": "10", "num": 1})
    with pytest.raises(exception.StopExtraction):
        data_job.handle_url("new", {"type": "video", "tweet_id": "11", "num": 1})
    assert output.events[0][0] == "candidate"
    assert output.events[0][2]["_source_url"] == "new"  # type: ignore[index]


def test_streaming_job_emits_invalid_identity_for_parent_contract_check() -> None:
    output = CapturingQueue()
    data_job = incremental._StreamingDataJob(
        "https://x.com/Reuters/timeline", 2, frozenset(), output
    )
    data_job.handle_url("new", {"type": "video", "tweet_id": "11", "num": "bad"})
    assert output.events[0][0] == "candidate"


@pytest.mark.parametrize("kind", ["anonymous", "firefox", "cookie_file"])
def test_worker_configuration_keeps_credentials_in_child_memory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, kind: str
) -> None:
    authentication: BrowserAuthentication | CookieFileAuthentication | None
    if kind == "anonymous":
        authentication = None
    elif kind == "firefox":
        authentication = BrowserAuthentication("firefox", "synthetic")
        monkeypatch.setattr(
            incremental, "load_firefox_x_cookies", lambda auth: {"auth_token": "a", "ct0": "c"}
        )
    else:
        cookie_file = tmp_path / "synthetic.cookies"
        cookie_file.write_text("# Netscape HTTP Cookie File\n")
        authentication = CookieFileAuthentication(cookie_file)
        monkeypatch.setattr(
            incremental,
            "load_cookie_file_x_cookies",
            lambda auth: {"auth_token": "a", "ct0": "c"},
        )
    incremental._configure_worker(authentication, 30)
    assert config.get(("extractor",), "timeout") == 30
    assert config.get(("extractor",), "download") is False
    assert config.get(("cache",), "file") == ":memory:"


def test_worker_main_reports_done_and_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    output = CapturingQueue()
    monkeypatch.setattr(incremental, "_configure_worker", lambda auth, timeout: None)

    class SuccessfulJob:
        emitted = 1

        def __init__(self, *args: object) -> None:
            pass

        def run(self) -> None:
            return None

    monkeypatch.setattr(incremental, "_StreamingDataJob", SuccessfulJob)
    incremental._worker_main("https://x.com/Reuters", 1, frozenset(), None, 30, output)
    assert output.events == [("done", 1)]

    class FailedJob(SuccessfulJob):
        def __init__(self, *args: object) -> None:
            raise RuntimeError("synthetic")

    monkeypatch.setattr(incremental, "_StreamingDataJob", FailedJob)
    incremental._worker_main("https://x.com/Reuters", 1, frozenset(), None, 30, output)
    assert output.events[-1] == ("failed",)


class FakeProcess:
    def __init__(self, target: Any, args: tuple[object, ...], *, alive: bool = False) -> None:
        self.target = target
        self.args = args
        self.alive = alive
        self.terminated = False
        self.killed = False
        self.joined = 0

    def start(self) -> None:
        self.target(*self.args)

    def is_alive(self) -> bool:
        return self.alive

    def terminate(self) -> None:
        self.terminated = True
        self.alive = False

    def kill(self) -> None:
        self.killed = True
        self.alive = False

    def join(self, timeout: float | None = None) -> None:
        del timeout
        self.joined += 1


class FakeContext:
    def __init__(self, output: CapturingQueue, *, alive: bool = False) -> None:
        self.output = output
        self.alive = alive
        self.process: FakeProcess | None = None

    def Queue(self) -> CapturingQueue:
        return self.output

    def Process(self, target: Any, args: tuple[object, ...]) -> FakeProcess:
        self.process = FakeProcess(target, args, alive=self.alive)
        return self.process


def test_incremental_provider_maps_candidate_and_joins_worker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = json.loads(FIXTURE.read_text())
    output = CapturingQueue()
    context = FakeContext(output)

    def worker(*args: object) -> None:
        queue_output = cast(CapturingQueue, args[-1])
        queue_output.put(("candidate", payload["profile_record"], payload["media_records"][0]))
        queue_output.put(("done", 1))

    monkeypatch.setattr(incremental, "_worker_main", worker)
    monkeypatch.setattr(
        "xma.adapters.discovery.incremental.multiprocessing.get_context",
        lambda method: context,
    )
    provider = incremental.IncrementalGalleryDlDiscoveryProvider()
    batches = list(provider.candidates(normalize_discovery_target("Reuters"), 1, frozenset(), 30))
    assert batches[0].asset_count == 1
    assert context.process is not None and context.process.joined == 1
    assert output.closed is True


def test_incremental_provider_timeout_terminates_and_joins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = CapturingQueue()
    context = FakeContext(output, alive=True)
    ticks = iter((0.0, 31.0))
    monkeypatch.setattr(incremental, "_worker_main", lambda *args: None)
    monkeypatch.setattr(
        "xma.adapters.discovery.incremental.multiprocessing.get_context",
        lambda method: context,
    )
    monkeypatch.setattr("xma.adapters.discovery.incremental.time.monotonic", lambda: next(ticks))
    provider = incremental.IncrementalGalleryDlDiscoveryProvider()
    with pytest.raises(DiscoveryTransientError, match="PROVIDER_TIMEOUT"):
        list(provider.candidates(normalize_discovery_target("Reuters"), 1, frozenset(), 30))
    assert context.process is not None
    assert context.process.terminated is True
    assert context.process.joined >= 1


def test_incremental_provider_fails_closed_off_linux(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("xma.adapters.discovery.incremental.sys.platform", "darwin")
    provider = incremental.IncrementalGalleryDlDiscoveryProvider()
    with pytest.raises(DiscoveryTransientError, match="PROVIDER_TIMEOUT"):
        list(provider.candidates(normalize_discovery_target("Reuters"), 1, frozenset(), 30))
