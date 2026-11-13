# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: Kiwix serves the downloaded Wikipedia snapshot (catalog, full-text search, article page)."""
import json
import os
import re
import urllib.parse
from pathlib import Path

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, run, step  # noqa: E402


def main() -> None:
    base = f"http://localhost:{port('WIKI_PORT', 8099)}"

    step("catalog lists at least one book")
    feed = http(f"{base}/catalog/v2/entries").body
    books = re.findall(r"/content/([^\"'/?]+)", feed)
    expect(books, "kiwix catalog has no books (did the downloader fetch any ZIM files?)")
    book = books[0]
    print(f"   book: {book}")

    step("manifest records a verified checksum")
    manifest_path = Path(os.environ.get("WIKI_DATA_DIR") or "data") / "wikipedia-manifest.json"
    if manifest_path.exists():
        files = json.loads(manifest_path.read_text(encoding="utf-8"))["files"]
        expect(files and all(f["status"] in ("verified", "no published checksum") for f in files.values()), f"unverified files in manifest: {files}")

    step("full-text search returns articles")
    html = http(f"{base}/search?content={urllib.parse.quote(book)}&pattern=virus").body
    links = re.findall(r'href="(/content/[^"]+)"', html)
    expect(links, "search for 'virus' returned no results")

    step("an article renders")
    page = http(base + links[0]).body
    expect(len(page) > 1000 and "<html" in page.lower(), "article page looks empty")


run(main)
