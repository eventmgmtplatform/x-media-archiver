"""B05 durable archive domain tests."""

from typing import Any

import pytest

from xma.domain.archive import ArchiveMode, ArchiveRequest
from xma.domain.errors import DomainError


@pytest.mark.parametrize("limit", [1, 10, 20])
def test_archive_request_accepts_boundary_totals(limit: int) -> None:
    assert ArchiveRequest.create("@BBCWorld", limit, 2, 1).requested_total == limit


@pytest.mark.parametrize("limit", [0, 21])
def test_archive_request_rejects_invalid_totals(limit: int) -> None:
    with pytest.raises(DomainError, match="between 1 and 20"):
        ArchiveRequest.create("BBCWorld", limit, 2, 1)


@pytest.mark.parametrize("batch", [0, 21])
def test_archive_request_rejects_invalid_batch(batch: int) -> None:
    with pytest.raises(DomainError, match="between 1 and 20"):
        ArchiveRequest.create("BBCWorld", 10, batch, 1)


@pytest.mark.parametrize("interval", [0, 61])
def test_archive_request_rejects_invalid_interval(interval: int) -> None:
    with pytest.raises(DomainError, match="between 1 and 60"):
        ArchiveRequest.create("BBCWorld", 10, 2, interval)


def test_archive_rejects_single_post() -> None:
    with pytest.raises(DomainError, match="profile targets only"):
        ArchiveRequest.create("https://x.com/BBCWorld/status/123", 10, 2, 1)


def test_all_request_has_explicit_mode_and_safety_controls() -> None:
    request = ArchiveRequest.create_all(
        "@BBCWorld",
        20,
        2,
        max_items=50,
        max_runtime_seconds=600,
        min_free_space_gib=5,
    )
    assert request.mode is ArchiveMode.ALL
    assert request.max_items == 50
    assert request.min_free_space_bytes == 5 * 1024**3


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_items": 0},
        {"max_runtime_seconds": 59},
        {"max_runtime_seconds": 21601},
        {"min_free_space_gib": 4},
        {"min_free_space_gib": 1025},
    ],
)
def test_all_request_rejects_invalid_safety_controls(kwargs: dict[str, Any]) -> None:
    with pytest.raises(DomainError):
        ArchiveRequest.create_all("BBCWorld", 5, 2, **kwargs)
