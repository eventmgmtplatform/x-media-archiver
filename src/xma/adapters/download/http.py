"""Streaming HTTPS media downloader for the bounded B04 slice."""

import hashlib
import mimetypes
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from xma.domain.download import DownloadedArtifact
from xma.domain.errors import DownloadError

_ALLOWED_EXTENSIONS = {".mp4", ".m4v", ".mov", ".webm"}


def _http_error_code(status: int) -> str:
    if status in {401, 403}:
        return "MEDIA_FORBIDDEN"
    if status in {404, 410}:
        return "MEDIA_URL_EXPIRED"
    if status == 408:
        return "MEDIA_TIMEOUT"
    if status == 429:
        return "MEDIA_RATE_LIMITED"
    if 500 <= status <= 599:
        return "MEDIA_SERVER_ERROR"
    return "MEDIA_DOWNLOAD_FAILED"


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
                raise DownloadError("MEDIA_CONTENT_INVALID")
            extension = Path(parsed.path).suffix.lower()
            if extension not in _ALLOWED_EXTENSIONS:
                guessed = mimetypes.guess_extension(mime_type) or ""
                extension = guessed if guessed in _ALLOWED_EXTENSIONS else ""
            if not extension or not mime_type.startswith(("video/", "audio/")):
                raise DownloadError("MEDIA_CONTENT_INVALID")
            return DownloadedArtifact(mime_type, size, digest.hexdigest(), extension)
        except DownloadError:
            destination.unlink(missing_ok=True)
            raise
        except HTTPError as error:
            destination.unlink(missing_ok=True)
            raise DownloadError(_http_error_code(error.code)) from error
        except TimeoutError as error:
            destination.unlink(missing_ok=True)
            raise DownloadError("MEDIA_TIMEOUT") from error
        except URLError as error:
            destination.unlink(missing_ok=True)
            raise DownloadError("MEDIA_CONNECTION_FAILED") from error
        except (OSError, ValueError) as error:
            destination.unlink(missing_ok=True)
            raise DownloadError("MEDIA_DOWNLOAD_FAILED") from error
