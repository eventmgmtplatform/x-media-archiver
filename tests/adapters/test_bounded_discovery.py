"""Offline tests for the Linux total discovery watchdog."""

import signal
from collections.abc import Callable
from typing import cast

import pytest

from xma.adapters.discovery.bounded import BoundedDiscoveryProvider
from xma.domain.discovery import DiscoveryBatch, DiscoveryTarget, normalize_discovery_target
from xma.domain.errors import DiscoveryTransientError


class Provider:
    def __init__(self, callback: Callable[[], DiscoveryBatch]) -> None:
        self.callback = callback

    def discover(self, target: DiscoveryTarget, limit: int) -> DiscoveryBatch:
        del target, limit
        return self.callback()


def test_watchdog_times_out_and_leaves_no_alarm() -> None:
    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)

    def expire() -> DiscoveryBatch:
        try:
            signal.raise_signal(signal.SIGALRM)
        except Exception as error:
            raise AssertionError("provider Exception handler swallowed deadline") from error
        raise AssertionError("deadline must interrupt discovery")

    provider = BoundedDiscoveryProvider(Provider(expire), 5)
    with pytest.raises(DiscoveryTransientError, match="PROVIDER_TIMEOUT"):
        provider.discover(normalize_discovery_target("Reuters"), 2)

    assert signal.getsignal(signal.SIGALRM) is previous_handler
    assert signal.getitimer(signal.ITIMER_REAL) == previous_timer


def test_watchdog_cancels_alarm_after_normal_success() -> None:
    marker = cast(DiscoveryBatch, object())
    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    provider = BoundedDiscoveryProvider(Provider(lambda: marker), 5)

    assert provider.discover(normalize_discovery_target("Reuters"), 2) is marker
    assert signal.getsignal(signal.SIGALRM) is previous_handler
    assert signal.getitimer(signal.ITIMER_REAL) == previous_timer


def test_watchdog_restores_prior_handler_and_timer(monkeypatch: pytest.MonkeyPatch) -> None:
    previous_handler = object()
    installed: list[object] = []
    timers: list[tuple[float, float]] = []

    monkeypatch.setattr(
        "xma.adapters.discovery.bounded.signal.getsignal", lambda signum: previous_handler
    )
    monkeypatch.setattr("xma.adapters.discovery.bounded.signal.getitimer", lambda which: (7.0, 2.0))
    monkeypatch.setattr(
        "xma.adapters.discovery.bounded.signal.signal",
        lambda signum, handler: installed.append(handler),
    )
    monkeypatch.setattr(
        "xma.adapters.discovery.bounded.signal.setitimer",
        lambda which, seconds, interval=0.0: timers.append((seconds, interval)),
    )

    marker = cast(DiscoveryBatch, object())
    provider = BoundedDiscoveryProvider(Provider(lambda: marker), 30)
    assert provider.discover(normalize_discovery_target("Reuters"), 2) is marker
    assert installed[-1] is previous_handler
    assert timers == [(30, 0.0), (0, 0.0), (7.0, 2.0)]


@pytest.mark.parametrize("seconds", [4, 61])
def test_watchdog_rejects_out_of_range_timeout(seconds: int) -> None:
    marker = cast(DiscoveryBatch, object())
    with pytest.raises(ValueError, match="between 5 and 60"):
        BoundedDiscoveryProvider(Provider(lambda: marker), seconds)


def test_watchdog_fails_closed_off_linux(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("xma.adapters.discovery.bounded.sys.platform", "darwin")
    marker = cast(DiscoveryBatch, object())
    provider = BoundedDiscoveryProvider(Provider(lambda: marker), 30)
    with pytest.raises(DiscoveryTransientError, match="PROVIDER_TIMEOUT"):
        provider.discover(normalize_discovery_target("Reuters"), 2)
