"""Offline tests for the contained Firefox authentication boundary."""

import sqlite3
from pathlib import Path

import pytest

from xma.adapters.discovery.firefox_auth import BrowserAuthentication, load_firefox_x_cookies
from xma.domain.errors import DiscoveryRestrictedError

SENSITIVE_MARKER = "SYNTHETIC-LOCAL-SESSION-MARKER"


def _firefox_root(
    tmp_path: Path,
    *,
    profile: str = "contained-profile",
    rows: tuple[tuple[str, str, str], ...] = (
        ("auth_token", "synthetic-auth-value", ".x.com"),
        ("ct0", "synthetic-csrf-value", "x.com"),
        ("unrelated", "must-not-load", ".example.com"),
    ),
) -> Path:
    root = tmp_path / "firefox"
    profile_directory = root / "Profiles" / "contained"
    profile_directory.mkdir(parents=True)
    (root / "profiles.ini").write_text(
        f"[Profile0]\nName={profile}\nIsRelative=1\nPath=Profiles/contained\n",
        encoding="utf-8",
    )
    with sqlite3.connect(profile_directory / "cookies.sqlite") as connection:
        connection.execute("CREATE TABLE moz_cookies(name TEXT, value TEXT, host TEXT)")
        connection.executemany("INSERT INTO moz_cookies VALUES (?, ?, ?)", rows)
    return root


def test_loads_only_x_domains_read_only_without_temporary_files(tmp_path: Path) -> None:
    root = _firefox_root(tmp_path)
    before = {path.relative_to(root) for path in root.rglob("*")}

    cookies = load_firefox_x_cookies(
        BrowserAuthentication("firefox", "contained-profile"), roots=(root,)
    )

    after = {path.relative_to(root) for path in root.rglob("*")}
    assert cookies == {"auth_token": "synthetic-auth-value", "ct0": "synthetic-csrf-value"}
    assert before == after
    assert not list(tmp_path.rglob("*.tmp"))


def test_uses_immutable_read_only_sqlite_uri(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    root = _firefox_root(tmp_path)
    real_connect = sqlite3.connect
    observed: list[tuple[str, bool]] = []

    def connect(database: str, *, uri: bool = False) -> sqlite3.Connection:
        observed.append((database, uri))
        return real_connect(database, uri=uri)

    monkeypatch.setattr("xma.adapters.discovery.firefox_auth.sqlite3.connect", connect)

    load_firefox_x_cookies(BrowserAuthentication("firefox", "contained-profile"), roots=(root,))

    assert len(observed) == 1
    assert observed[0][1] is True
    assert observed[0][0].endswith("?mode=ro&immutable=1")


def test_reader_failure_is_constant_sanitized_and_has_no_fallback(
    caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    root = _firefox_root(tmp_path, profile=SENSITIVE_MARKER, rows=())
    before = {path.relative_to(root) for path in root.rglob("*")}

    with pytest.raises(DiscoveryRestrictedError) as captured:
        load_firefox_x_cookies(BrowserAuthentication("firefox", SENSITIVE_MARKER), roots=(root,))

    assert str(captured.value) == "authenticated Firefox session is unavailable"
    assert captured.value.__cause__ is None
    assert SENSITIVE_MARKER not in str(captured.value) + caplog.text
    assert before == {path.relative_to(root) for path in root.rglob("*")}


@pytest.mark.parametrize(
    "profile",
    [
        "",
        ".",
        "..",
        " profile",
        "profile name",
        "profile\n",
        "/absolute",
        "../escape",
        "dir/profile",
        "dir\\profile",
        "_leading-symbol",
        "a" * 129,
    ],
)
def test_profile_selector_rejects_non_contained_names(profile: str) -> None:
    with pytest.raises(ValueError, match="browser authentication configuration is invalid"):
        BrowserAuthentication("firefox", profile)


def test_exact_inventory_entry_is_required(tmp_path: Path) -> None:
    root = _firefox_root(tmp_path)

    with pytest.raises(
        DiscoveryRestrictedError, match="authenticated Firefox session is unavailable"
    ):
        load_firefox_x_cookies(BrowserAuthentication("firefox", "other-profile"), roots=(root,))


def test_symlink_escape_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "firefox"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "cookies.sqlite").write_bytes(b"not-used")
    (root / "escaped").symlink_to(outside, target_is_directory=True)
    (root / "profiles.ini").write_text(
        "[Profile0]\nName=contained-profile\nIsRelative=1\nPath=escaped\n",
        encoding="utf-8",
    )

    with pytest.raises(
        DiscoveryRestrictedError, match="authenticated Firefox session is unavailable"
    ):
        load_firefox_x_cookies(BrowserAuthentication("firefox", "contained-profile"), roots=(root,))
