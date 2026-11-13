#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Resolve, download, verify and inspect Wikipedia ZIM snapshots for kiwix-serve.

Python 3.10+ standard library only, so it runs identically on Linux, macOS and Windows, on the host or
inside the ``downloader`` container (mount the data directory either way).

Dataset specs (comma separated in WIKI_DATASETS or as positional arguments):
    sample                     English, 100 most popular articles with images   (~320 MB)  DEFAULT
    top-mini | top-nopic | top-maxi      English, top articles: intro only / no images / full   (0.3 / 2.6 / 6.5 GB)
    all-mini | all-nopic | all-maxi      English, ALL articles: intro only / no images / full   (13 / 49 / 119 GB)
    [lang:]set[:flavour]       e.g. ``fr:all:nopic``, ``de:top:mini``, ``en:100``
    wikipedia_en_100_2026-08.zim        an exact file name (pins a snapshot; the mirror only keeps recent ones)

Commands:
    list [--lang en] [--grep TEXT]      what the mirror offers right now
    plan [SPEC ...]                     resolve specs to concrete files and sizes (downloads nothing)
    download [SPEC ...]                 download (resumable), verify SHA-256, update the manifest
    verify                              re-hash every ZIM in the data dir against its published SHA-256
    status                              show files and the manifest

Common options / environment:
    --dir DIR      WIKI_DATA_DIR   where ZIM files live (default ./data; /data in the container)
    WIKI_MIRROR                    default https://download.kiwix.org/zim/wikipedia/
    WIKI_DATASETS                  default specs when none are given (default "sample")
    HTTPS_PROXY / HTTP_PROXY       honoured automatically; SSL_CERT_FILE for a corporate CA bundle
    WIKI_INSECURE=1                skip TLS verification (last resort behind a TLS-inspecting proxy)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import ssl
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MIRROR = "https://download.kiwix.org/zim/wikipedia/"
MANIFEST = "wikipedia-manifest.json"
USER_AGENT = "containerising-wikipedia/1.0"
CHUNK = 1024 * 1024
SAFETY_MARGIN = 1024**3  # keep 1 GiB free after downloading

PRESETS = {
    "sample": ("en", "100", None),
    "top-mini": ("en", "top", "mini"),
    "top-nopic": ("en", "top", "nopic"),
    "top-maxi": ("en", "top", "maxi"),
    "all-mini": ("en", "all", "mini"),
    "all-nopic": ("en", "all", "nopic"),
    "all-maxi": ("en", "all", "maxi"),
}
FLAVOURS = {"maxi", "nopic", "mini"}
NAME_RE = re.compile(
    r"^wikipedia_(?P<lang>[a-z]{2,3}(?:-[a-z0-9]+)*)_(?P<set>[a-z0-9]+?)(?:_(?P<flavour>maxi|nopic|mini))?_(?P<date>\d{4}-\d{2})\.zim$"
)
LINK_RE = re.compile(r'<a href="(wikipedia_[^"/]+\.zim)">')


class WikiError(Exception):
    """User-facing error (printed without a traceback)."""


@dataclass(frozen=True)
class Entry:
    name: str
    lang: str
    set: str
    flavour: str | None
    date: str


# --------------------------------------------------------------------------- networking
def _opener() -> urllib.request.OpenerDirector:
    ctx = ssl.create_default_context()  # OS trust store (also on Windows) / SSL_CERT_FILE
    if os.environ.get("WIKI_INSECURE") == "1":
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))  # proxies come from the env


def _request(url: str, *, method: str = "GET", headers: dict[str, str] | None = None, timeout: float = 60):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT, **(headers or {})})
    return _opener().open(req, timeout=timeout)


def _get_text(url: str) -> str:
    try:
        with _request(url) as r:
            return r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as e:
        raise WikiError(f"cannot fetch {url}: {e}\n  (behind a proxy? set HTTPS_PROXY; custom CA? set SSL_CERT_FILE)") from e


def _content_length(url: str) -> int | None:
    try:
        with _request(url, method="HEAD") as r:
            v = r.headers.get("Content-Length")
            return int(v) if v else None
    except (urllib.error.URLError, OSError, ValueError):
        return None


# --------------------------------------------------------------------------- resolution
def mirror_url() -> str:
    m = os.environ.get("WIKI_MIRROR") or DEFAULT_MIRROR
    return m if m.endswith("/") else m + "/"


def parse_name(name: str) -> Entry | None:
    m = NAME_RE.match(name)
    return Entry(name, m["lang"], m["set"], m["flavour"], m["date"]) if m else None


def fetch_catalog(mirror: str) -> list[Entry]:
    html = _get_text(mirror)
    entries = [e for e in (parse_name(n) for n in sorted(set(LINK_RE.findall(html)))) if e]
    if not entries:
        raise WikiError(f"no Wikipedia ZIM files found at {mirror}")
    return entries


def parse_spec(spec: str) -> tuple[str, str, str | None] | str:
    """Return (lang, set, flavour), or an exact file name."""
    spec = spec.strip()
    if spec.endswith(".zim"):
        return spec
    if spec in PRESETS:
        return PRESETS[spec]
    parts = spec.split(":")
    if len(parts) == 1:  # "100" / "top" / "all" -> English
        parts = ["en", parts[0]]
    if len(parts) == 2:
        lang, set_ = parts
        flavour = None if set_ == "100" else "mini"
    elif len(parts) == 3:
        lang, set_, flavour = parts
    else:
        raise WikiError(f"bad dataset spec {spec!r}")
    if flavour and flavour not in FLAVOURS:
        raise WikiError(f"bad flavour {flavour!r} in {spec!r} (use maxi, nopic or mini)")
    return lang, set_, flavour


def resolve(spec: str, catalog: list[Entry]) -> Entry:
    parsed = parse_spec(spec)
    if isinstance(parsed, str):
        for e in catalog:
            if e.name == parsed:
                return e
        raise WikiError(f"{parsed} is not on the mirror any more (it keeps only recent snapshots); run `list` to see what exists")
    lang, set_, flavour = parsed
    matches = [e for e in catalog if e.lang == lang and e.set == set_ and e.flavour == flavour]
    if not matches:
        have = sorted({f"{e.lang}:{e.set}" + (f":{e.flavour}" if e.flavour else "") for e in catalog if e.lang == lang})
        raise WikiError(f"no snapshot for {spec!r}; available for {lang!r}: {', '.join(have) or 'none'}")
    return max(matches, key=lambda e: e.date)


def specs_from(args_specs: list[str]) -> list[str]:
    raw = args_specs or (os.environ.get("WIKI_DATASETS") or "sample").split(",")
    return [s.strip() for s in raw if s.strip()] or ["sample"]


# --------------------------------------------------------------------------- manifest / files
def data_dir(args: argparse.Namespace) -> Path:
    return Path(args.dir or os.environ.get("WIKI_DATA_DIR") or "data").resolve()


def load_manifest(d: Path) -> dict:
    p = d / MANIFEST
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"files": {}}


def save_manifest(d: Path, m: dict) -> None:
    tmp = d / (MANIFEST + ".tmp")
    tmp.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, d / MANIFEST)


def ensure_writable(d: Path) -> None:
    try:
        d.mkdir(parents=True, exist_ok=True)
        probe = d / ".write-test"
        probe.write_text("x")
        probe.unlink()
    except OSError as e:
        raise WikiError(
            f"data directory {d} is not writable ({e}).\n"
            "  Linux/Docker: create it yourself (mkdir data) and run the container as your user "
            "(set WIKI_UID and WIKI_GID to your ids), or run this script on the host."
        ) from e


def sha256_file(path: Path, label: str = "") -> str:
    h = hashlib.sha256()
    total = max(path.stat().st_size, 1)
    done, last = 0, time.monotonic()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
            done += len(chunk)
            if label and time.monotonic() - last > 10:
                print(f"  hashing {label}: {done / total:6.1%}", flush=True)
                last = time.monotonic()
    return h.hexdigest()


def published_sha256(url: str) -> str | None:
    try:
        text = _get_text(url + ".sha256")
    except WikiError:
        return None
    m = re.match(r"\s*([0-9a-fA-F]{64})\b", text)
    return m.group(1).lower() if m else None


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n} B"


# --------------------------------------------------------------------------- download
def download_file(url: str, dest: Path, expected_size: int | None, retries: int = 6) -> None:
    part = dest.with_name(dest.name + ".part")
    attempt = 0
    while True:
        have = part.stat().st_size if part.exists() else 0
        headers = {"Range": f"bytes={have}-"} if have else {}
        try:
            with _request(url, headers=headers, timeout=60) as r:
                if have and r.status != 206:
                    have = 0  # server ignored Range: start over
                total = expected_size or (have + int(r.headers.get("Content-Length") or 0)) or None
                done, started, last = have, time.monotonic(), 0.0
                with open(part, "ab" if have else "wb") as f:
                    while chunk := r.read(CHUNK):
                        f.write(chunk)
                        done += len(chunk)
                        now = time.monotonic()
                        if now - last > 15:
                            rate = (done - have) / max(now - started, 1e-6)
                            pct = f"{done / total:6.1%}" if total else "   ?  "
                            eta = f"  eta {int((total - done) / rate / 60)} min" if total and rate > 0 else ""
                            print(f"  {dest.name}: {pct}  {human(done)}{' / ' + human(total) if total else ''}  {human(rate)}/s{eta}", flush=True)
                            last = now
            if expected_size and part.stat().st_size != expected_size:
                raise OSError(f"incomplete download ({part.stat().st_size} of {expected_size} bytes)")
            os.replace(part, dest)
            return
        except (urllib.error.URLError, OSError) as e:
            if isinstance(e, urllib.error.HTTPError) and e.code == 416 and part.exists():  # range past EOF: already complete
                os.replace(part, dest)
                return
            attempt += 1
            if attempt > retries:
                raise WikiError(f"download failed after {retries} retries: {e}") from e
            wait = min(60, 2**attempt)
            print(f"  ! {e}; retrying in {wait}s (attempt {attempt}/{retries}, resumable)", flush=True)
            time.sleep(wait)


def present_offline(d: Path, specs: list[str], manifest: dict) -> list[str] | None:
    """Files already on disk for every spec (matched through the manifest), or None if any is missing."""
    found = []
    for spec in specs:
        names = [n for n, info in manifest["files"].items()
                 if (info.get("spec") == spec or n == spec) and (d / n).exists() and not (d / n).with_name(n + ".part").exists()]
        if not names:
            return None
        found.append(sorted(names)[-1])
    return found


def cmd_download(args: argparse.Namespace) -> int:
    d = data_dir(args)
    ensure_writable(d)
    mirror = mirror_url()
    manifest = load_manifest(d)
    specs = specs_from(args.datasets)
    try:
        catalog = fetch_catalog(mirror)
    except WikiError as e:
        # Mirror unreachable (offline, or a TLS-inspecting proxy the container does not trust):
        # that is fine if everything requested was downloaded earlier (e.g. on the host).
        have = present_offline(d, specs, manifest)
        if have is None:
            raise
        reason = str(e).splitlines()[0]
        print(f"warning: mirror unreachable ({reason}); using files already in {d}: {', '.join(have)}", flush=True)
        return 0
    for spec in specs:
        e = resolve(spec, catalog)
        url = mirror + e.name
        dest = d / e.name
        part = dest.with_name(dest.name + ".part")
        size = _content_length(url)
        print(f"== {spec}: {e.name} ({human(size) if size else 'size unknown'})", flush=True)
        complete = dest.exists() and size is not None and dest.stat().st_size == size
        if complete and e.name in manifest["files"]:
            print("  already present (size matches manifest); use `verify` to re-hash")
            continue
        if not complete:
            need = (size or 0) - (part.stat().st_size if part.exists() else 0)
            free = shutil.disk_usage(d).free
            if size and not args.no_space_check and free < need + SAFETY_MARGIN:
                raise WikiError(f"not enough disk space in {d}: need {human(need + SAFETY_MARGIN)}, free {human(free)} (--no-space-check to override)")
            download_file(url, dest, size)
        expected = published_sha256(url)
        if args.no_verify:
            digest, status = None, "unverified"
        else:
            print("  verifying SHA-256 ...", flush=True)
            digest = sha256_file(dest, dest.name)
            if expected and digest != expected:
                dest.replace(dest.with_name(dest.name + ".corrupt"))
                raise WikiError(f"checksum mismatch for {e.name}: got {digest}, published {expected}; moved aside as .corrupt")
            status = "verified" if expected else "no published checksum"
        manifest["files"][e.name] = {
            "spec": spec, "url": url, "bytes": dest.stat().st_size, "sha256": digest or expected,
            "status": status, "resolved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        save_manifest(d, manifest)
        print(f"  ok: {status}", flush=True)
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    mirror = mirror_url()
    catalog = fetch_catalog(mirror)
    d = data_dir(args)
    total = 0
    for spec in specs_from(args.datasets):
        e = resolve(spec, catalog)
        size = _content_length(mirror + e.name) or 0
        present = (d / e.name).exists()
        total += 0 if present else size
        print(f"{spec:12} -> {e.name}  {human(size) if size else '?':>9}  {'present' if present else 'to download'}")
    free = shutil.disk_usage(d if d.exists() else d.parent).free
    print(f"to download: {human(total)}; free in {d}: {human(free)}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    latest: dict[tuple, Entry] = {}
    for e in fetch_catalog(mirror_url()):
        if args.lang and e.lang != args.lang:
            continue
        if args.grep and args.grep not in e.name:
            continue
        k = (e.lang, e.set, e.flavour)
        if k not in latest or e.date > latest[k].date:
            latest[k] = e
    for k in sorted(latest, key=lambda k: (k[0], k[1], k[2] or "")):
        e = latest[k]
        print(f"{e.lang}:{e.set}" + (f":{e.flavour}" if e.flavour else "") + f"  ->  {e.name}")
    print(f"\n{len(latest)} datasets (latest snapshot of each); the mirror keeps only recent snapshots", file=sys.stderr)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    d = data_dir(args)
    zims = sorted(d.glob("*.zim"))
    if not zims:
        raise WikiError(f"no .zim files in {d}")
    manifest, bad = load_manifest(d), 0
    for z in zims:
        want = (manifest["files"].get(z.name) or {}).get("sha256") or published_sha256(mirror_url() + z.name)
        got = sha256_file(z, z.name)
        state = "OK" if want and got == want else ("UNKNOWN" if not want else "MISMATCH")
        bad += state == "MISMATCH"
        print(f"{state:8} {z.name}  {got}")
    return 1 if bad else 0


def cmd_status(args: argparse.Namespace) -> int:
    d = data_dir(args)
    print(f"data dir: {d}")
    m = load_manifest(d)
    zims = sorted(d.glob("*.zim")) if d.exists() else []
    for z in zims:
        print(f"  {z.name}  {human(z.stat().st_size)}  {(m['files'].get(z.name) or {}).get('status', 'not in manifest')}")
    for p in sorted(d.glob("*.part")) if d.exists() else []:
        print(f"  {p.name}  {human(p.stat().st_size)}  (partial, resumable)")
    if not zims:
        print("  no ZIM files yet: run `download`")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", help="data directory (env WIKI_DATA_DIR, default ./data)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn, help_ in (("plan", cmd_plan, "resolve specs, show sizes"), ("download", cmd_download, "download + verify")):
        p = sub.add_parser(name, help=help_)
        p.add_argument("datasets", nargs="*")
        p.set_defaults(fn=fn)
        if name == "download":
            p.add_argument("--no-verify", action="store_true", help="skip SHA-256 verification")
            p.add_argument("--no-space-check", action="store_true")
    p = sub.add_parser("list", help="list datasets on the mirror")
    p.add_argument("--lang")
    p.add_argument("--grep")
    p.set_defaults(fn=cmd_list)
    for name, fn in (("verify", cmd_verify), ("status", cmd_status)):
        sub.add_parser(name).set_defaults(fn=fn)
    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except WikiError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ninterrupted (partial downloads are kept and resumable)", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
