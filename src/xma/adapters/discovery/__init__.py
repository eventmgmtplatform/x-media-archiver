"""Public discovery adapter exports."""

from xma.adapters.discovery.bounded import BoundedDiscoveryProvider
from xma.adapters.discovery.firefox_auth import BrowserAuthentication, CookieFileAuthentication
from xma.adapters.discovery.gallery_dl import GalleryDlDiscoveryProvider
from xma.adapters.discovery.incremental import IncrementalGalleryDlDiscoveryProvider

__all__ = [
    "BoundedDiscoveryProvider",
    "BrowserAuthentication",
    "CookieFileAuthentication",
    "GalleryDlDiscoveryProvider",
    "IncrementalGalleryDlDiscoveryProvider",
]
