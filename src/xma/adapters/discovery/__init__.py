"""Public discovery adapter exports."""

from xma.adapters.discovery.firefox_auth import BrowserAuthentication, CookieFileAuthentication
from xma.adapters.discovery.gallery_dl import GalleryDlDiscoveryProvider

__all__ = ["BrowserAuthentication", "CookieFileAuthentication", "GalleryDlDiscoveryProvider"]
