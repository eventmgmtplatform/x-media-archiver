"""Offline tests for the streaming HTTP media adapter."""

from email.message import Message
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest

from xma.adapters.download.http import HttpMediaDownloadProvider
from xma.domain.errors import DownloadError


class Response:
    def __init__(self, payload: bytes, mime_type: str = "video/mp4") -> None:
        self.payload = payload
        self.offset = 0
        self.headers = Message()
        self.headers["Content-Type"] = mime_type

    def __enter__(self) -> "Response":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self, size: int) -> bytes:
        chunk = self.payload[self.offset : self.offset + size]
        self.offset += len(chunk)
        return chunk


def test_streams_nonempty_media_to_part_and_returns_checksum(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = b"synthetic-video-payload"
    monkeypatch.setattr(
        "xma.adapters.download.http.urlopen",
        lambda request, timeout: Response(payload),
    )
    part = tmp_path / "video.part"

    result = HttpMediaDownloadProvider().download(
        "https://media.invalid/video.mp4?private=query",
        str(part),
    )

    assert part.read_bytes() == payload
    assert result.mime_type == "video/mp4"
    assert result.extension == ".mp4"
    assert result.size_bytes == len(payload)
    assert len(result.sha256) == 64


def test_empty_or_invalid_media_fails_and_removes_part(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        "xma.adapters.download.http.urlopen",
        lambda request, timeout: Response(b""),
    )
    part = tmp_path / "video.part"

    with pytest.raises(DownloadError, match="MEDIA_CONTENT_INVALID"):
        HttpMediaDownloadProvider().download("https://media.invalid/video.mp4", str(part))
    assert not part.exists()

    with pytest.raises(DownloadError, match="media download failed"):
        HttpMediaDownloadProvider().download("http://media.invalid/video.mp4", str(part))


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (401, "MEDIA_FORBIDDEN"),
        (403, "MEDIA_FORBIDDEN"),
        (404, "MEDIA_URL_EXPIRED"),
        (410, "MEDIA_URL_EXPIRED"),
        (408, "MEDIA_TIMEOUT"),
        (429, "MEDIA_RATE_LIMITED"),
        (500, "MEDIA_SERVER_ERROR"),
        (503, "MEDIA_SERVER_ERROR"),
    ],
)
def test_http_status_is_sanitized(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, status: int, code: str
) -> None:
    def fail(request: object, timeout: int) -> object:
        raise HTTPError("https://secret.invalid/?token=private", status, "raw", Message(), None)

    monkeypatch.setattr("xma.adapters.download.http.urlopen", fail)
    part = tmp_path / "video.part"
    with pytest.raises(DownloadError, match=code) as captured:
        HttpMediaDownloadProvider().download("https://media.invalid/video.mp4", str(part))
    assert "secret" not in str(captured.value)
    assert not part.exists()


@pytest.mark.parametrize(
    ("error", "code"),
    [(TimeoutError(), "MEDIA_TIMEOUT"), (URLError("private"), "MEDIA_CONNECTION_FAILED")],
)
def test_transport_error_is_sanitized(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, error: OSError, code: str
) -> None:
    def fail(request: object, timeout: int) -> object:
        raise error

    monkeypatch.setattr("xma.adapters.download.http.urlopen", fail)
    with pytest.raises(DownloadError, match=code):
        HttpMediaDownloadProvider().download(
            "https://media.invalid/video.mp4", str(tmp_path / "video.part")
        )
