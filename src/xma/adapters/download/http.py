"""Streaming HTTPS media downloader for the bounded B04 slice."""

import hashlib
import mimetypes
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from xma.domain.download import DownloadedArtifact
from xma.domain.errors import DownloadError

_ALLOWED_EXTENSIONS = {".mp4", ".m4v", ".mov", ".webm"}


class HttpMediaDownloadProvider:
    """Download one ephemeral HTTPS media URL without retaining the URL."""

    def download(self, source_url: str, part_path: str) -> DownloadedArtifact:
        parsed = urlparse(source_url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise DownloadError("media download failed")
        destination = Path(part_path)
        digest = hashlib.sha256()
        size = 0
        try:
            request = Request(source_url, headers={"User-Agent": "x-media-archiver/0.1"})
            with urlopen(request, timeout=60) as response, destination.open("xb") as stream:
                mime_type = response.headers.get_content_type().lower()
                for chunk in iter(lambda: response.read(1024 * 1024), b""):
                    stream.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
            if size == 0:
                raise DownloadError("media download failed")
            extension = Path(parsed.path).suffix.lower()
            if extension not in _ALLOWED_EXTENSIONS:
                guessed = mimetypes.guess_extension(mime_type) or ""
                extension = guessed if guessed in _ALLOWED_EXTENSIONS else ""
            if not extension or not mime_type.startswith(("video/", "audio/")):
                raise DownloadError("media download failed")
            return DownloadedArtifact(mime_type, size, digest.hexdigest(), extension)
        except DownloadError:
            destination.unlink(missing_ok=True)
            raise
        except (OSError, ValueError) as error:
            destination.unlink(missing_ok=True)
            raise DownloadError("media download failed") from error
