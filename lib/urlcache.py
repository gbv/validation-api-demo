from pathlib import Path
import hashlib
import requests
import json


class URLCache(object):
    """HTTP GET requests with response cached in a directory of the file system."""

    def __init__(self, dir: str):
        """Create a new cache at given directory."""
        self.dir = Path(dir)
        if not self.dir.is_dir():
            raise FileNotFoundError(f"Missing cache directory: {dir}")

    def hash(self, url: str) -> str:
        """Get the hash value of an URL."""
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def entry(self, url: str) -> dict:
        """Get the cached entry for an URL, if existing."""
        hash = self.hash(url)
        meta_file = self.dir / f"{hash}.json"

        if meta_file.exists():
            return json.loads(meta_file.read_text(encoding="utf-8"))

    def fetch(self, url: str, cached=True):
        """Perform a HTTP Request or get URL from the cache."""
        hash = self.hash(url)
        body_file = self.dir / hash
        meta_file = self.dir / f"{hash}.json"

        if cached and body_file.exists():
            meta = self.entry(url)
            if meta:
                body = body_file.read_bytes()
            return body_file, meta

        response = requests.get(url)
        response.raise_for_status()
        body = response.content
        meta = dict(response.headers)

        meta['url'] = url
        meta['hash'] = hash
        body_file.write_bytes(body)
        meta['cached'] = body_file.stat().st_mtime
        meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        return body_file, meta
