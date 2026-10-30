"""B05 durable archive domain tests."""

import pytest

from xma.domain.archive import ArchiveRequest
from xma.domain.errors import DomainError


@pytest.mark.parametrize("limit", [1, 10, 20])
def test_archive_request_accepts_boundary_totals(limit: int) -> None:
    assert ArchiveRequest.create("@BBCWorld", limit, 2, 1).requested_total == limit


@pytest.mark.parametrize("limit", [0, 21])
def test_archive_request_rejects_invalid_totals(limit: int) -> None:
    with pytest.raises(DomainError, match="between 1 and 20"):
        ArchiveRequest.create("BBCWorld", limit, 2, 1)


@pytest.mark.parametrize("batch", [0, 6])
def test_archive_request_rejects_invalid_batch(batch: int) -> None:
    with pytest.raises(DomainError, match="between 1 and 5"):
        ArchiveRequest.create("BBCWorld", 10, batch, 1)


@pytest.mark.parametrize("interval", [0, 61])
def test_archive_request_rejects_invalid_interval(interval: int) -> None:
    with pytest.raises(DomainError, match="between 1 and 60"):
        ArchiveRequest.create("BBCWorld", 10, 2, interval)


def test_archive_rejects_single_post() -> None:
    with pytest.raises(DomainError, match="profile targets only"):
        ArchiveRequest.create("https://x.com/BBCWorld/status/123", 10, 2, 1)
