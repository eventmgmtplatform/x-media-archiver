"""Offline Pipe/DTO tests for incremental gallery-dl discovery."""

import json
import pickle
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import pytest
from gallery_dl import config, exception  # type: ignore[import-untyped]

import xma.adapters.discovery.incremental as incremental
from xma.adapters.discovery.firefox_auth import BrowserAuthentication, CookieFileAuthentication
from xma.domain.discovery import normalize_discovery_target
from xma.domain.errors import DiscoveryContractError, DiscoveryTransientError

FIXTURE = Path(__file__).parents[1] / "fixtures/gallery_dl/twitter_videos.json"


class Connection:
    def __init__(self, messages: list[dict[str, Any]] | None = None) -> None:
        self.messages = list(messages or [])
        self.closed = False

    def send(self, message: dict[str, Any]) -> None:
        self.messages.append(message)

    def poll(self, timeout: float = 0) -> bool:
        del timeout
        return bool(self.messages)

    def recv(self) -> dict[str, Any]:
        if not self.messages:
            raise EOFError
        return self.messages.pop(0)

    def close(self) -> None:
        self.closed = True


def _post(**updates: object) -> dict[str, object]:
    result: dict[str, object] = {
        "tweet_id": "11",
        "author": {"id": "123"},
        "num": 1,
        "type": "video",
        "duration": 1.5,
        "width": 1280,
        "height": 720,
        "content": "synthetic",
        "date": datetime(2026, 1, 2, tzinfo=UTC),
        "retweet_id": None,
        "quoted_id": None,
        "reply_id": None,
    }
    result.update(updates)
    return result


def test_explicit_dto_is_primitive_serializes_date_and_ignores_extra() -> None:
    dto = incremental._candidate_dto(
        "https://example.invalid/media",
        _post(extra=object(), author={"id": "123", "ignored": object()}),
    )
    assert incremental._is_ipc_primitive(dto)
    assert dto["date"] == "2026-01-02T00:00:00+00:00"
    assert "extra" not in dto
    assert dto["author"] == {"id": "123"}


def test_primitive_validator_and_send_reject_invalid_shapes() -> None:
    assert incremental._is_ipc_primitive(("ok", [1, True, None]))
    assert not incremental._is_ipc_primitive({1: "invalid"})
    assert not incremental._is_ipc_primitive(object())
    with pytest.raises(ValueError):
        incremental._send(cast(Any, Connection()), {"bad": float("nan")})


def test_profile_dto_rejects_required_nonprimitive() -> None:
    with pytest.raises(ValueError):
        incremental._profile_dto({"user": {"id": object()}})


@pytest.mark.parametrize("field,value", [("author", object()), ("width", float("inf"))])
def test_required_nonprimitive_is_rejected_without_content(field: str, value: object) -> None:
    with pytest.raises(ValueError, match="^$"):
        incremental._candidate_dto("ephemeral", _post(**{field: value}))


def test_streaming_job_sends_candidate_before_stop_and_skips_duplicate() -> None:
    output = Connection()
    data_job = incremental._StreamingDataJob.__new__(incremental._StreamingDataJob)
    data_job.remaining = 1
    data_job.existing = frozenset({"10:0"})
    data_job.output = cast(Any, output)
    data_job.profile_record = None
    data_job.videos_seen = data_job.duplicates_skipped = data_job.emitted = 0
    data_job.handle_directory(
        {
            "user": {
                "id": "123",
                "name": "Example",
                "nick": "example",
                "protected": False,
            },
            "ignored": object(),
        }
    )
    data_job.handle_url("old", cast(Any, _post(tweet_id="10")))
    with pytest.raises(exception.StopExtraction):
        data_job.handle_url("new", cast(Any, _post(tweet_id="11")))
    kinds = [item["kind"] for item in output.messages]
    assert kinds[-2:] == ["candidate", "telemetry"]
    assert output.messages[-2]["post"]["source_url"] == "new"
    assert any(item.get("event") == "DUPLICATE_SKIPPED" for item in output.messages)


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
            incremental, "load_cookie_file_x_cookies", lambda auth: {"auth_token": "a", "ct0": "c"}
        )
    incremental._configure_worker(authentication, 30)
    assert config.get(("extractor",), "timeout") == 30
    assert config.get(("extractor",), "download") is False
    assert config.get(("cache",), "file") == ":memory:"


@pytest.mark.parametrize(
    "mode,terminal",
    [
        ("success", "COMPLETED"),
        ("empty", "PROVIDER_EXHAUSTED"),
        ("failure", "WORKER_FAILED"),
        ("invalid", "IPC_SERIALIZATION_FAILED"),
    ],
)
def test_worker_terminal_classification(
    monkeypatch: pytest.MonkeyPatch, mode: str, terminal: str
) -> None:
    output = Connection()
    monkeypatch.setattr(incremental, "_configure_worker", lambda auth, timeout: None)

    class Job:
        emitted = 1 if mode == "success" else 0

        def __init__(self, *args: object) -> None:
            if mode == "failure":
                raise RuntimeError("secret")
            if mode == "invalid":
                raise ValueError("secret")

        def run(self) -> None:
            return None

    monkeypatch.setattr(incremental, "_StreamingDataJob", Job)
    incremental._worker_main("https://example.invalid", 1, frozenset(), None, 30, cast(Any, output))
    assert output.messages[-1] == {"version": 1, "kind": "terminal", "status": terminal}
    assert output.closed
    assert "secret" not in json.dumps(output.messages)


class Process:
    def __init__(self, target: Any, args: tuple[object, ...], alive: bool) -> None:
        self.target, self.args, self.alive = target, args, alive
        self.terminated = self.killed = False
        self.joined = 0

    def start(self) -> None:
        if not self.alive:
            self.target(*self.args)

    def is_alive(self) -> bool:
        return self.alive

    def terminate(self) -> None:
        self.terminated, self.alive = True, False

    def kill(self) -> None:
        self.killed, self.alive = True, False

    def join(self, timeout: float | None = None) -> None:
        del timeout
        self.joined += 1


class Context:
    def __init__(self, receiver: Connection, sender: Connection, alive: bool = False) -> None:
        self.receiver, self.sender, self.alive = receiver, sender, alive
        self.process: Process | None = None

    def Pipe(self, duplex: bool) -> tuple[Connection, Connection]:
        assert duplex is False
        return self.receiver, self.sender

    def Process(self, target: Any, args: tuple[object, ...]) -> Process:
        self.process = Process(target, args, self.alive)
        return self.process


def _provider(
    monkeypatch: pytest.MonkeyPatch,
    messages: list[dict[str, Any]],
    *,
    alive: bool = False,
    telemetry: list[str] | None = None,
) -> tuple[incremental.IncrementalGalleryDlDiscoveryProvider, Context]:
    receiver, sender = Connection(messages), Connection()
    context = Context(receiver, sender, alive)
    monkeypatch.setattr(incremental, "_worker_main", lambda *args: None)

    def get_context(method: str) -> Context:
        assert method == "spawn"
        return context

    monkeypatch.setattr(
        "xma.adapters.discovery.incremental.multiprocessing.get_context", get_context
    )
    sink = telemetry if telemetry is not None else []
    return incremental.IncrementalGalleryDlDiscoveryProvider(telemetry=sink.append), context


def test_spawn_target_and_authentication_are_importable_and_serializable() -> None:
    assert incremental._worker_main.__module__ == "xma.adapters.discovery.incremental"
    authentication = BrowserAuthentication("firefox", "synthetic")
    restored = pickle.loads(pickle.dumps(authentication))
    assert restored == authentication
    assert not hasattr(restored, "auth_token")
    assert not hasattr(restored, "ct0")


def test_provider_maps_candidate_then_completed_and_closes_pipe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = json.loads(FIXTURE.read_text())
    post = incremental._candidate_dto(
        payload["media_records"][0]["_source_url"], payload["media_records"][0]
    )
    messages = [
        {"version": 1, "kind": "telemetry", "event": "VIDEO_SEEN", "videos_seen": 1},
        {
            "version": 1,
            "kind": "candidate",
            "profile": incremental._profile_dto(payload["profile_record"]),
            "post": post,
        },
        {"version": 1, "kind": "terminal", "status": "COMPLETED"},
    ]
    telemetry: list[str] = []
    provider, context = _provider(monkeypatch, messages, telemetry=telemetry)
    batches = list(provider.candidates(normalize_discovery_target("Reuters"), 1, frozenset(), 30))
    assert batches[0].asset_count == 1
    assert telemetry == ["worker VIDEO_SEEN videos_seen=1"]
    assert context.receiver.closed and context.sender.closed
    assert context.process is not None and context.process.joined == 1


@pytest.mark.parametrize(
    "terminal,error",
    [
        ("PROVIDER_EXHAUSTED", DiscoveryTransientError),
        ("WORKER_FAILED", DiscoveryContractError),
        ("IPC_SERIALIZATION_FAILED", DiscoveryContractError),
    ],
)
def test_provider_terminal_errors(
    monkeypatch: pytest.MonkeyPatch, terminal: str, error: type[Exception]
) -> None:
    provider, _ = _provider(monkeypatch, [{"version": 1, "kind": "terminal", "status": terminal}])
    with pytest.raises(error, match=terminal):
        list(provider.candidates(normalize_discovery_target("Reuters"), 1, frozenset(), 30))


def test_eof_without_terminal_is_worker_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    provider, _ = _provider(monkeypatch, [])
    with pytest.raises(DiscoveryContractError, match="WORKER_FAILED"):
        list(provider.candidates(normalize_discovery_target("Reuters"), 1, frozenset(), 30))


def test_timeout_with_live_worker_terminates_and_joins(monkeypatch: pytest.MonkeyPatch) -> None:
    provider, context = _provider(monkeypatch, [], alive=True)
    ticks = iter((0.0, 31.0))
    monkeypatch.setattr("xma.adapters.discovery.incremental.time.monotonic", lambda: next(ticks))
    with pytest.raises(DiscoveryTransientError, match="PROVIDER_TIMEOUT"):
        list(provider.candidates(normalize_discovery_target("Reuters"), 1, frozenset(), 30))
    assert context.process is not None and context.process.terminated and context.process.joined


def test_provider_fails_closed_off_linux(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("xma.adapters.discovery.incremental.sys.platform", "darwin")
    with pytest.raises(DiscoveryTransientError, match="PROVIDER_TIMEOUT"):
        list(
            incremental.IncrementalGalleryDlDiscoveryProvider().candidates(
                normalize_discovery_target("Reuters"), 1, frozenset(), 30
            )
        )
