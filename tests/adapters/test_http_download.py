"""Offline tests for the streaming HTTP media adapter."""

from email.message import Message
from pathlib import Path

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

    with pytest.raises(DownloadError, match="media download failed"):
        HttpMediaDownloadProvider().download("https://media.invalid/video.mp4", str(part))
    assert not part.exists()

    with pytest.raises(DownloadError, match="media download failed"):
        HttpMediaDownloadProvider().download("http://media.invalid/video.mp4", str(part))
