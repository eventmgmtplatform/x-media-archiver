"""Contained, read-only Firefox session loading for X discovery."""

import configparser
import os
import re
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from xma.domain.errors import DiscoveryRestrictedError

_PROFILE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_AUTH_CONFIGURATION_ERROR = "browser authentication configuration is invalid"
_AUTH_SESSION_ERROR = "authenticated Firefox session is unavailable"
_X_COOKIE_HOSTS = ("x.com", ".x.com", "twitter.com", ".twitter.com")


@dataclass(frozen=True, slots=True)
class BrowserAuthentication:
    """Local browser-session selector; cookie values never cross infrastructure."""

    browser: str
    profile: str

    def __post_init__(self) -> None:
        if self.browser.casefold() != "firefox":
            raise ValueError(_AUTH_CONFIGURATION_ERROR)
        if (
            not _PROFILE_NAME.fullmatch(self.profile)
            or self.profile in {".", ".."}
            or any(character.isspace() or not character.isprintable() for character in self.profile)
        ):
            raise ValueError(_AUTH_CONFIGURATION_ERROR)
        object.__setattr__(self, "browser", "firefox")


def load_firefox_x_cookies(
    authentication: BrowserAuthentication,
    *,
    roots: tuple[Path, ...] | None = None,
) -> dict[str, str]:
    """Load only X cookie values through a contained, immutable SQLite connection."""
    try:
        database = _resolve_cookie_database(authentication.profile, roots or _firefox_roots())
        uri = f"file:{quote(database.as_posix(), safe='/')}?mode=ro&immutable=1"
        with closing(sqlite3.connect(uri, uri=True)) as connection:
            connection.execute("PRAGMA query_only = ON")
            rows = connection.execute(
                "SELECT name, value FROM moz_cookies WHERE host IN (?, ?, ?, ?)",
                _X_COOKIE_HOSTS,
            ).fetchall()
        cookies = {str(name): str(value) for name, value in rows}
        if not cookies:
            raise ValueError(_AUTH_SESSION_ERROR)
        return cookies
    except (configparser.Error, OSError, sqlite3.Error, ValueError):
        raise DiscoveryRestrictedError(_AUTH_SESSION_ERROR) from None


def _firefox_roots() -> tuple[Path, ...]:
    home = Path.home()
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
    return (
        config_home / "mozilla/firefox",
        home / ".mozilla/firefox",
        home / ".var/app/org.mozilla.firefox/config/mozilla/firefox",
        home / ".var/app/org.mozilla.firefox/.mozilla/firefox",
        home / "snap/firefox/common/.mozilla/firefox",
    )


def _resolve_cookie_database(profile: str, roots: tuple[Path, ...]) -> Path:
    matches: list[Path] = []
    for candidate_root in roots:
        try:
            root = candidate_root.resolve(strict=True)
            inventory = (root / "profiles.ini").resolve(strict=True)
        except OSError:
            continue
        if not inventory.is_relative_to(root) or not inventory.is_file():
            continue
        parser = configparser.ConfigParser(interpolation=None)
        with inventory.open(encoding="utf-8") as stream:
            parser.read_file(stream)
        for section in parser.sections():
            if (
                not section.startswith("Profile")
                or parser.get(section, "Name", fallback="") != profile
            ):
                continue
            path_value = parser.get(section, "Path", fallback="")
            if not path_value:
                raise ValueError(_AUTH_SESSION_ERROR)
            configured = Path(path_value)
            profile_directory = (
                root / configured
                if parser.getboolean(section, "IsRelative", fallback=True)
                else configured
            ).resolve(strict=True)
            if not profile_directory.is_relative_to(root) or not profile_directory.is_dir():
                raise ValueError(_AUTH_SESSION_ERROR)
            database = (profile_directory / "cookies.sqlite").resolve(strict=True)
            if not database.is_relative_to(profile_directory) or not database.is_file():
                raise ValueError(_AUTH_SESSION_ERROR)
            matches.append(database)
    if len(matches) != 1:
        raise ValueError(_AUTH_SESSION_ERROR)
    return matches[0]
