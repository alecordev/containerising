# Wikipedia (local, offline copy)

A local, searchable copy of Wikipedia served by [Kiwix](https://kiwix.org) (`kiwix-serve`). Wikipedia is stored as compressed **ZIM** snapshots; Kiwix serves them with browsing and full-text search, no database import needed.

The data download is automated and **reproducible**: a stdlib-only Python tool resolves the latest snapshot, downloads it with resume, verifies its SHA-256 against the one the mirror publishes, and records what it fetched in a manifest. The tool runs inside the `downloader` container or directly on your machine, against any directory you mount.

```
wikipedia/
  docker-compose.yml   downloader (one-shot) -> kiwix (server)
  Dockerfile           target "downloader" (python:3.14-slim) and target "server" (kiwix-serve)
  prep/wiki.py         resolve / download / verify tool (Python 3.10+, stdlib only, cross-OS)
  smoke.py             live check used by scripts/smoke.py With the stack already running, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run wikipedia/smoke.py`).
  .env.example         every setting, with defaults
  data/                ZIM files + wikipedia-manifest.json (created on first run, git-ignored)
```

## Run

```bash
docker compose up -d --wait        # first run downloads the default "sample" dataset (~320 MB)
```

Open **http://localhost:8099** and use the search box. Stop with `docker compose down` (the data stays in `./data`).

Change what you download with `WIKI_DATASETS` (shell, `.env`, or `--env-file`):

```bash
# PowerShell:  $env:WIKI_DATASETS="top-nopic"; docker compose up -d --wait
# bash/zsh:    WIKI_DATASETS=top-nopic docker compose up -d --wait
# any shell:   put WIKI_DATASETS=top-nopic in .env
```

## Datasets

| Spec | What you get | Size (Nov 2026) |
|---|---|---|
| `sample` (default) | English, the 100 most popular articles, with images | ~0.3 GB |
| `top-mini` / `top-nopic` / `top-maxi` | English, popular articles: intro only / no images / full | 0.3 / 2.6 / 6.5 GB |
| `all-mini` / `all-nopic` / `all-maxi` | English, **all** articles: intro only / no images / full | 13 / 49 / 119 GB |
| `fr:all:nopic`, `de:top:mini`, `en:100`, ... | `[lang:]set[:flavour]` for any language/set on the mirror | varies |
| `wikipedia_en_100_2026-08.zim` | an exact file name (pins a snapshot) | varies |

Combine several with commas (`WIKI_DATASETS=sample,fr:top:mini`); Kiwix serves every `.zim` in the data directory. List what exists with `uv run prep/wiki.py list --lang en` (other sets include topic collections such as chemistry or astronomy).

## Using the tool directly (no container)

The same script works on the host, which is also the easiest way past a corporate proxy or for huge downloads you want to run natively:

```bash
uv run prep/wiki.py list --lang fr          # what the mirror offers
uv run prep/wiki.py plan all-nopic          # resolve + show sizes and free disk, download nothing
uv run prep/wiki.py download top-mini       # resumable; verifies SHA-256; updates the manifest
uv run prep/wiki.py status                  # files, sizes, verification state
uv run prep/wiki.py verify                  # re-hash everything against the published checksums
```

The script is standard library only, so `python prep/wiki.py ...` works as well; `uv run` just picks a suitable Python (3.10+) for you.

The data directory defaults to `./data` (`--dir` or `WIKI_DATA_DIR` to change it). To start the server from files you downloaded on the host, skip the downloader:

```bash
docker compose up -d --wait --no-deps kiwix
```

Mount any directory by setting `WIKI_DATA_DIR` (for example `WIKI_DATA_DIR=D:/wikipedia`); it is mounted writable for the downloader and read-only for Kiwix.

## Reproducibility

- **The mirror keeps only recent snapshots**, so "latest" moves every month or two. The downloader resolves the newest snapshot at run time and records the exact file, URL, size, SHA-256 and timestamp in `data/wikipedia-manifest.json`.
- To pin a snapshot, use its exact file name in `WIKI_DATASETS`. If the mirror has dropped it, the tool says so; keep the downloaded `data/` directory as your archive (copy it between machines).
- Files are verified against the checksum published next to each ZIM; a mismatch is moved aside as `.corrupt` and the run fails.
- The server image is pinned (`ghcr.io/kiwix/kiwix-serve:3.8.2`, `KIWIX_VERSION`) and so is the downloader's Python (`PYTHON_VERSION`).
- Re-running is cheap: files already present (size matches the manifest) are skipped, and if the mirror is unreachable the downloader proceeds when everything requested is already on disk.

## Settings

| Variable | Default | Description |
|---|---|---|
| `WIKI_DATASETS` | `sample` | Comma separated dataset specs (see above) |
| `WIKI_PORT` | `8099` | Host port for the Kiwix web UI |
| `WIKI_DATA_DIR` | `./data` | Host directory for ZIM files and the manifest |
| `WIKI_MIRROR` | `https://download.kiwix.org/zim/wikipedia/` | Download mirror |
| `WIKI_UID` / `WIKI_GID` | `10001` | User the downloader runs as (Linux: set to your ids) |
| `KIWIX_VERSION`, `PYTHON_VERSION` | `3.8.2`, `3.14` | Image versions |
| `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY` | from your shell | Forwarded to the downloader |
| `WIKI_INSECURE` | `0` | `1` skips TLS verification (last resort) |

## Notes and troubleshooting

- **Disk space**: the tool checks free space before downloading and stops early with a clear message. The full English edition (`all-maxi`) needs ~120 GB, and you need roughly 2x during download plus checksum on slow filesystems.
- **Linux permissions**: Docker creates `./data` as root. Create it yourself and set `WIKI_UID`/`WIKI_GID` to your ids (or run `uv run prep/wiki.py download` on the host). Docker Desktop on Windows/macOS needs nothing.
- **Behind a corporate proxy with TLS inspection**: the container does not trust your corporate CA and may not reach a proxy bound to `localhost`. Download on the host instead (`uv run prep/wiki.py download`, which uses your OS trust store and `HTTPS_PROXY`), then `docker compose up -d --wait`: the downloader sees the files are present and exits successfully.
- **Interrupted downloads** resume automatically (`.part` files are kept); just run it again.
- **Large downloads**: `docker compose up --wait` blocks until the download finishes. For multi-GB sets run `uv run prep/wiki.py download <spec>` first and watch its progress.
- **Not covered**: a full MediaWiki + database import from the XML dumps (hours of processing, hundreds of GB). Kiwix serves the same content read-only, which is what most local-copy needs are. Add a MediaWiki template if you need editing or the API.

## Smoke test

```bash
python ../scripts/smoke.py wikipedia
```

Checks the catalog, the manifest's verification status, a full-text search and an article render. It uses the default `sample` dataset (and the data already in `./data`).

## Resources

- Kiwix: https://kiwix.org, `kiwix-serve` docs: https://github.com/kiwix/kiwix-tools
- ZIM mirror: https://download.kiwix.org/zim/wikipedia/
- Container image: https://github.com/kiwix/kiwix-tools/pkgs/container/kiwix-serve
