"""Public discovery adapter exports."""

from xma.adapters.discovery.bounded import BoundedDiscoveryProvider
from xma.adapters.discovery.firefox_auth import BrowserAuthentication, CookieFileAuthentication
from xma.adapters.discovery.gallery_dl import GalleryDlDiscoveryProvider

__all__ = [
    "BoundedDiscoveryProvider",
    "BrowserAuthentication",
    "CookieFileAuthentication",
    "GalleryDlDiscoveryProvider",
]
