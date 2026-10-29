"""Offline tests for the contained Firefox authentication boundary."""

import sqlite3
from pathlib import Path

import pytest

from xma.adapters.discovery.firefox_auth import (
    BrowserAuthentication,
    CookieFileAuthentication,
    load_cookie_file_x_cookies,
    load_firefox_x_cookies,
)
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
    "rows",
    [
        (),
        (("ct0", "synthetic-csrf-value", "x.com"),),
        (("auth_token", "synthetic-auth-value", ".x.com"),),
        (
            ("auth_token", "", ".x.com"),
            ("ct0", "synthetic-csrf-value", "x.com"),
        ),
        (
            ("auth_token", "synthetic-auth-value", ".x.com"),
            ("ct0", "", "x.com"),
        ),
    ],
    ids=["empty", "ct0-only", "auth-token-only", "empty-auth-token", "empty-ct0"],
)
def test_incomplete_session_fails_closed_without_exposing_values(
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
    rows: tuple[tuple[str, str, str], ...],
) -> None:
    root = _firefox_root(tmp_path, rows=rows)

    with pytest.raises(DiscoveryRestrictedError) as captured:
        load_firefox_x_cookies(
            BrowserAuthentication("firefox", "contained-profile"),
            roots=(root,),
        )

    public_text = str(captured.value) + caplog.text
    assert public_text == "authenticated Firefox session is unavailable"
    assert "synthetic-auth-value" not in public_text
    assert "synthetic-csrf-value" not in public_text


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


def test_circular_symlink_is_rejected_with_sanitized_contract(
    caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    marker = "SYNTHETIC-CIRCULAR-PATH-MARKER"
    root = tmp_path / "firefox"
    root.mkdir()
    circular = root / marker
    circular.symlink_to(circular)
    (root / "profiles.ini").write_text(
        f"[Profile0]\nName=contained-profile\nIsRelative=1\nPath={marker}\n",
        encoding="utf-8",
    )

    with pytest.raises(DiscoveryRestrictedError) as captured:
        load_firefox_x_cookies(
            BrowserAuthentication("firefox", "contained-profile"),
            roots=(root,),
        )

    assert str(captured.value) == "authenticated Firefox session is unavailable"
    assert captured.value.__cause__ is None
    assert marker not in str(captured.value) + caplog.text


def test_netscape_cookie_file_loads_x_session_without_exposure(tmp_path: Path) -> None:
    marker = "SYNTHETIC-COOKIE-VALUE-MARKER"
    cookie_file = tmp_path / "local.cookies"
    cookie_file.write_text(
        "# Netscape HTTP Cookie File\n"
        f".x.com\tTRUE\t/\tTRUE\t0\tauth_token\t{marker}-auth\n"
        f"x.com\tFALSE\t/\tTRUE\t0\tct0\t{marker}-ct0\n"
        f".example.com\tTRUE\t/\tTRUE\t0\tunrelated\t{marker}-other\n",
        encoding="utf-8",
    )

    cookies = load_cookie_file_x_cookies(CookieFileAuthentication(cookie_file))

    assert cookies == {
        "auth_token": f"{marker}-auth",
        "ct0": f"{marker}-ct0",
    }


@pytest.mark.parametrize("kind", ["missing", "directory", "symlink"])
def test_cookie_file_rejects_nonlocal_file(tmp_path: Path, kind: str) -> None:
    path = tmp_path / "cookies.txt"
    if kind == "directory":
        path.mkdir()
    elif kind == "symlink":
        target = tmp_path / "target.txt"
        target.write_text("not used", encoding="utf-8")
        path.symlink_to(target)

    with pytest.raises(ValueError, match="browser authentication configuration is invalid"):
        CookieFileAuthentication(path)


def test_incomplete_cookie_file_error_is_sanitized(
    caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    marker = "SYNTHETIC-COOKIE-VALUE-MARKER"
    cookie_file = tmp_path / "local.cookies"
    cookie_file.write_text(
        f"# Netscape HTTP Cookie File\nx.com\tFALSE\t/\tTRUE\t0\tct0\t{marker}\n",
        encoding="utf-8",
    )

    with pytest.raises(DiscoveryRestrictedError) as captured:
        load_cookie_file_x_cookies(CookieFileAuthentication(cookie_file))

    assert str(captured.value) == "authenticated Firefox session is unavailable"
    assert marker not in str(captured.value) + caplog.text
