import pytest
import time
from unittest.mock import patch, MagicMock
from tempfile import TemporaryDirectory
from lib.urlcache import URLCache


def test_config():
    with pytest.raises(FileNotFoundError, match="Missing cache directory: ./missing/directory"):
        URLCache("./missing/directory")


def test_urlcache():
    url = "http://example.org"
    response = MagicMock()
    response.status_code = 200
    response.content = b"Hello, world!"
    response.headers = {"Content-Type": "text/plain"}
    response.raise_for_status = MagicMock()

    with TemporaryDirectory() as path:
        cache = URLCache(path)

        assert cache.entry(url) is None

        with patch("lib.urlcache.requests.get") as mock_get:
            mock_get.return_value = response

            # cache miss => request.get was called
            body_file, meta = cache.fetch(url)
            mock_get.assert_called_once_with(url)
            assert body_file.exists()
            assert body_file.read_bytes() == response.content
            assert meta["url"] == url
            assert meta["Content-Type"] == "text/plain"
            assert meta["hash"] == cache.hash(url)
            assert meta["cached"] <= time.time()

            # reset call count and fetch again => request.get was not called
            mock_get.reset_mock()
            body_file_cached, meta_cached = cache.fetch(url)
            mock_get.assert_not_called()
            assert body_file_cached == body_file
            assert meta_cached == meta

            # Fetch again with cached=False => requests.get was called again
            body_file_fresh, meta_fresh = cache.fetch(url, cached=False)
            mock_get.assert_called_once_with(url)
            assert body_file_fresh == body_file
            assert cache.entry(url) == meta_fresh
            meta["cached"] = meta_fresh["cached"]  # timestamp changed
            assert meta_fresh == meta

            # called internally to raise an execption if request failed
            response.raise_for_status.assert_called_once()
