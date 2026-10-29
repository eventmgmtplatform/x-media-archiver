"""Linux total-deadline boundary for one complete discovery operation."""

import signal
import sys
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from types import FrameType

from xma.domain.discovery import DiscoveryBatch, DiscoveryTarget
from xma.domain.errors import DiscoveryError, DiscoveryTransientError
from xma.domain.ports import DiscoveryProvider


class _DiscoveryDeadlineExceeded(BaseException):
    """Private signal that provider ``except Exception`` blocks cannot swallow."""


@contextmanager
def _linux_discovery_watchdog(seconds: int) -> Iterator[None]:
    if sys.platform != "linux" or threading.current_thread() is not threading.main_thread():
        raise DiscoveryTransientError("temporary provider failure [PROVIDER_TIMEOUT]")

    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    handler_installed = False
    timer_armed = False

    def expire(signum: int, frame: FrameType | None) -> None:
        del signum, frame
        raise _DiscoveryDeadlineExceeded

    try:
        signal.signal(signal.SIGALRM, expire)
        handler_installed = True
        signal.setitimer(signal.ITIMER_REAL, seconds)
        timer_armed = True
        yield
    except _DiscoveryDeadlineExceeded as error:
        raise DiscoveryTransientError("temporary provider failure [PROVIDER_TIMEOUT]") from error
    finally:
        if timer_armed:
            signal.setitimer(signal.ITIMER_REAL, 0)
        if handler_installed:
            signal.signal(signal.SIGALRM, previous_handler)
        if previous_timer != (0.0, 0.0):
            signal.setitimer(signal.ITIMER_REAL, *previous_timer)


class BoundedDiscoveryProvider:
    """Apply one Linux wall-clock deadline to an entire provider call."""

    def __init__(
        self,
        provider: DiscoveryProvider,
        timeout_seconds: int,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if timeout_seconds < 5 or timeout_seconds > 60:
            raise ValueError("discovery timeout must be between 5 and 60 seconds")
        self._provider = provider
        self._timeout_seconds = timeout_seconds
        self._clock = clock or time.monotonic

    def discover(self, target: DiscoveryTarget, limit: int) -> DiscoveryBatch:
        started = self._clock()
        try:
            with _linux_discovery_watchdog(self._timeout_seconds):
                result = self._provider.discover(target, limit)
        except DiscoveryError as error:
            if self._clock() - started >= self._timeout_seconds:
                raise DiscoveryTransientError(
                    "temporary provider failure [PROVIDER_TIMEOUT]"
                ) from error
            raise
        if self._clock() - started >= self._timeout_seconds:
            raise DiscoveryTransientError("temporary provider failure [PROVIDER_TIMEOUT]")
        return result
