"""Bounded GitHub release discovery and verified, explicitly requested downloads.

The GUI never installs in place. An independent native helper waits for it to exit
and starts Inno; Inno owns patch compatibility and final file verification.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, HTTPRedirectHandler, build_opener

from app_paths import APP_DIR, STATE_DIR

REPO = "zcm58/Necker-Studio"
API = f"https://api.github.com/repos/{REPO}/releases"
PREFIX = "Nicholas-Nice-Necker-Cube-Experiment"
APP_GUID = "{5FC7235D-8D03-4668-9F37-508A1B481689}"
REG_KEY = rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP_GUID}_is1"
MAX_BYTES = 2 * 1024**3
CACHE = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "NicholasNiceNeckerCubeExperiment" / "updates"


class UpdateError(RuntimeError):
    pass


class Cancelled(UpdateError):
    pass


def check_cancel(cancel):
    if cancel is not None and cancel.is_set():
        raise Cancelled("Update cancelled.")


def version_key(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{1,5}\.\d{1,5}(?:\.\d{1,5})?", value):
        raise UpdateError("Invalid release version.")
    return tuple(int(p) for p in value.split(".")) + (0,) * (3 - len(value.split(".")))


def current_version(app=APP_DIR):
    release = app / "release.json"
    if release.is_file():
        value = json.loads(release.read_text(encoding="utf-8"))["version"]
    else:
        import tomllib
        value = tomllib.loads((app / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    version_key(value)
    return value


def load_preferences():
    try:
        value = json.loads((STATE_DIR / "updates.json").read_text(encoding="utf-8"))
        return {"automatic": value.get("automatic") is not False}
    except (OSError, ValueError, AttributeError):
        return {"automatic": True}


def save_preferences(automatic):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = STATE_DIR / "updates.json"
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps({"automatic": bool(automatic)}), encoding="utf-8")
    temporary.replace(path)


def safe_path(path, *, file=False):
    """Reject linked cache/install paths; no recursive cleanup ever uses these paths."""
    path = Path(path).absolute()
    for part in (*reversed(path.parents), path):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise UpdateError("Linked update or installation paths are not supported.")
        if part != path and not stat.S_ISDIR(info.st_mode):
            raise UpdateError("Invalid update directory.")
        if part == path and file and (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
            raise UpdateError("Update files must be regular files with one link.")
    return path


def registered_install(app=APP_DIR):
    if sys.platform != "win32" or not (app / "release.json").is_file():
        return None
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
            root = Path(winreg.QueryValueEx(key, "InstallLocation")[0])
            version = winreg.QueryValueEx(key, "DisplayVersion")[0]
        if root.resolve() != app.parent.resolve() or version != current_version(app):
            return None
        safe_path(root)
        if Path(sys.executable).resolve().parent != (root / "runtime").resolve():
            return None
        return root
    except (OSError, ValueError, UpdateError):
        return None


def _url(url, *, asset=False):
    parsed = urlparse(url)
    allowed = {"api.github.com"} if not asset else {"api.github.com", "github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com"}
    if parsed.scheme != "https" or parsed.hostname not in allowed or parsed.username or parsed.password or parsed.port not in (None, 443) or parsed.fragment:
        raise UpdateError("An update URL is outside the trusted GitHub boundary.")
    return parsed


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _url(newurl, asset=True)
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None and urlparse(newurl).hostname != "api.github.com":
            redirected.remove_header("Authorization")
        return redirected


def _open(url, token, binary):
    _url(url)
    headers = {"User-Agent": "Necker-Experiment-Updater", "Accept": "application/octet-stream" if binary else "application/vnd.github+json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    return build_opener(SafeRedirect()).open(Request(url, headers=headers), timeout=5)


def _transfer(url, *, token="", limit, output, cancel=None, progress=None, binary=False):
    started, count = time.monotonic(), 0
    try:
        with _open(url, token, binary) as response:
            _url(response.geturl(), asset=binary)
            while True:
                check_cancel(cancel)
                if time.monotonic() - started > (1800 if binary else 30):
                    raise UpdateError("The update request exceeded its time limit.")
                chunk = response.read(256 * 1024)
                if not chunk:
                    break
                count += len(chunk)
                if count > limit:
                    raise UpdateError("GitHub returned more data than the declared update size.")
                output(chunk)
                if progress:
                    progress(count, limit)
    except HTTPError as error:
        if error.code in (401, 403, 404):
            raise UpdateError("GitHub could not provide this release. The service may be rate-limited or temporarily unavailable; try again later.") from None
        raise UpdateError(f"GitHub request failed (HTTP {error.code}).") from None
    except (URLError, TimeoutError, OSError):
        raise UpdateError("Could not reach GitHub. Check the connection and try again.") from None
    check_cancel(cancel)
    return count


def _json(url, token, cancel):
    data = bytearray()
    _transfer(url, token=token, limit=2 * 1024**2, output=data.extend, cancel=cancel)
    try:
        return json.loads(data)
    except (ValueError, UnicodeError):
        raise UpdateError("GitHub returned invalid release metadata.") from None


@dataclass(frozen=True)
class Asset:
    name: str
    asset_id: int
    size: int
    digest: str
    version: str
    kind: str = "full"
    from_version: str = ""

    @property
    def api_url(self):
        return API + f"/assets/{self.asset_id}"


@dataclass(frozen=True)
class Release:
    version: str
    asset: Asset | None
    full: Asset | None
    reason: str = ""


def parse_asset(raw, name, version, kind="full", from_version=""):
    if not isinstance(raw, dict) or raw.get("name") != name or raw.get("state") != "uploaded":
        raise UpdateError("Release asset identity does not match its version.")
    digest = raw.get("digest", "")
    if not isinstance(digest, str) or not re.fullmatch(r"sha256:[a-fA-F0-9]{64}", digest):
        raise UpdateError("This release is available, but its GitHub SHA-256 is missing. Download is disabled.")
    asset_id, size = raw.get("id"), raw.get("size")
    if type(asset_id) is not int or asset_id <= 0 or type(size) is not int or not 0 < size <= MAX_BYTES:
        raise UpdateError("Invalid release asset size or identifier.")
    if raw.get("url") != API + f"/assets/{asset_id}":
        raise UpdateError("Release asset is from another repository.")
    return Asset(name, asset_id, size, digest[7:].lower(), version, kind, from_version)


def select_release(releases, current):
    if not isinstance(releases, list):
        raise UpdateError("Invalid GitHub release list.")
    candidates = []
    for release in releases:
        if not isinstance(release, dict) or release.get("draft") or release.get("prerelease"):
            continue
        try:
            version = release.get("tag_name", "").removeprefix("v")
            key = version_key(version)
        except (UpdateError, AttributeError):
            continue
        if key > version_key(current):
            candidates.append((key, version, release))
    if not candidates:
        return None, None
    _, version, raw = max(candidates, key=lambda item: item[0])
    assets = raw.get("assets", [])
    if not isinstance(assets, list):
        raise UpdateError("Invalid release assets.")
    matches = [a for a in assets if isinstance(a, dict) and a.get("name") == f"{PREFIX}-Setup-{version}-x64.exe"]
    if len(matches) != 1:
        return Release(version, None, None, "The full Windows installer is not available yet."), raw
    try:
        full = parse_asset(matches[0], matches[0]["name"], version)
        return Release(version, full, full), raw
    except UpdateError as error:
        return Release(version, None, None, str(error)), raw


def choose_patch(release, raw, document, current, inventory_digest):
    if not isinstance(document, dict) or document.get("schema_version") != 1 or document.get("target_version") != release.version or document.get("platform") != "windows-x64" or not isinstance(document.get("patches"), list):
        raise UpdateError("Invalid patch metadata; no package will be installed.")
    candidates = []
    seen = set()
    for item in document["patches"]:
        if not isinstance(item, dict):
            raise UpdateError("Invalid patch entry.")
        source = item.get("from_version")
        if version_key(source) >= version_key(release.version) or source in seen:
            raise UpdateError("Invalid or duplicate patch source version.")
        seen.add(source)
        name = f"{PREFIX}-Patch-{source}-to-{release.version}-x64.exe"
        matches = [a for a in raw["assets"] if isinstance(a, dict) and a.get("name") == name]
        if len(matches) != 1:
            raise UpdateError("Patch metadata refers to a missing package.")
        asset = parse_asset(matches[0], name, release.version, "patch", source)
        if item.get("asset_name") != name or item.get("size_bytes") != asset.size or item.get("sha256") != asset.digest or not re.fullmatch(r"[0-9a-f]{64}", str(item.get("source_inventory_sha256", ""))):
            raise UpdateError("Patch metadata does not match GitHub's package identity.")
        if source == current and item["source_inventory_sha256"] == inventory_digest and release.full and asset.size < release.full.size:
            candidates.append(asset)
    if candidates:
        return Release(release.version, min(candidates, key=lambda a: a.size), release.full,
                       "Patch compatibility will be checked during installation.")
    return Release(release.version, release.full, release.full, "No compatible patch; the full installer is available.")


def check_for_updates(*, token="", cancel=None, app=APP_DIR, force_full=False):
    current = current_version(app)
    release, raw = select_release(_json(API + "?per_page=30", token, cancel), current)
    if release is None or release.full is None or force_full:
        return release
    root = registered_install(app)
    if root is None:
        return release
    matches = [a for a in raw["assets"] if isinstance(a, dict) and a.get("name") == f"{PREFIX}-Update-{release.version}.json"]
    if not matches:
        return release
    if len(matches) != 1:
        raise UpdateError("Duplicate patch metadata.")
    metadata = parse_asset(matches[0], matches[0]["name"], release.version)
    if metadata.size > 1024**2:
        raise UpdateError("Patch metadata is too large.")
    data = bytearray()
    size = _transfer(metadata.api_url, token=token, limit=metadata.size, output=data.extend, cancel=cancel, binary=True)
    if size != metadata.size or hashlib.sha256(data).hexdigest() != metadata.digest:
        raise UpdateError("Patch metadata failed verification.")
    try:
        document = json.loads(data)
    except (ValueError, UnicodeError):
        raise UpdateError("Invalid patch metadata.") from None
    inventory = root / "manifest.json"
    try:
        safe_path(inventory, file=True)
        if inventory.stat().st_size > 16 * 1024**2:
            raise UpdateError("Installed inventory is too large.")
        digest = hashlib.sha256(inventory.read_bytes()).hexdigest()
    except OSError:
        digest = ""
    return choose_patch(release, raw, document, current, digest)


@contextmanager
def cache_lock(cache=CACHE):
    safe_path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    path = safe_path(cache / "update.lock", file=True)
    with path.open("a+b") as lock:
        lock.seek(0)
        if sys.platform == "win32":
            import msvcrt
            try:
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                raise UpdateError("Another update is already in progress.") from None
        try:
            yield
        finally:
            if sys.platform == "win32":
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


def _prune(cache, keep=None):
    for path in cache.iterdir():
        if re.fullmatch(r"(?:download-[0-9a-f]{64}\.exe(?:\.part)?|helper-[0-9a-f]{64}\.exe)", path.name) and path != keep:
            safe_path(path, file=True)
            path.unlink()


def cleanup_cache(cache=CACHE):
    if not cache.exists():
        return
    try:
        with cache_lock(cache):
            _prune(cache)
    except (OSError, UpdateError):
        pass  # A running helper owns the cache; leave it alone.


def hash_file(path, cancel=None):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024**2):
            check_cancel(cancel)
            digest.update(chunk)
    return digest.hexdigest()


def refresh_asset(asset, token, cancel):
    raw = _json(API + f"/tags/v{asset.version}", token, cancel)
    if not isinstance(raw, dict) or raw.get("draft") or raw.get("prerelease") or raw.get("tag_name") != "v" + asset.version:
        raise UpdateError("This release is no longer eligible.")
    matches = [a for a in raw.get("assets", []) if isinstance(a, dict) and a.get("name") == asset.name]
    if len(matches) != 1 or parse_asset(matches[0], asset.name, asset.version, asset.kind, asset.from_version) != asset:
        raise UpdateError("The selected release asset changed. Check for updates again.")


def download(asset, *, token="", cancel=None, progress=None, cache=CACHE):
    refresh_asset(asset, token, cancel)
    with cache_lock(cache):
        target = safe_path(cache / f"download-{asset.digest}.exe", file=True)
        _prune(cache, keep=target)
        if target.exists() and target.stat().st_size == asset.size and hash_file(target, cancel) == asset.digest:
            return target
        partial = safe_path(target.with_suffix(".exe.part"), file=True)
        try:
            with partial.open("xb") as stream:
                size = _transfer(asset.api_url, token=token, limit=asset.size, output=stream.write, cancel=cancel, progress=progress, binary=True)
            if size != asset.size or hash_file(partial, cancel) != asset.digest:
                raise UpdateError("The download failed its size or SHA-256 check. Please retry.")
            check_cancel(cancel)
            partial.replace(target)
            return target
        finally:
            if partial.exists():
                partial.unlink()


def begin_install(asset, path, *, token="", cancel=None, app=APP_DIR, cache=CACHE):
    """Return only after an independently running helper accepts explicit installation."""
    root = registered_install(app)
    if root is None:
        raise UpdateError("Install updates from the installed application. PyCharm source files are not replaced.")
    refresh_asset(asset, token, cancel)
    if version_key(asset.version) <= version_key(current_version(app)):
        raise UpdateError("The selected update is no longer newer.")
    if asset.kind == "patch" and asset.from_version != current_version(app):
        raise UpdateError("The patch no longer matches this installation.")
    path = safe_path(path, file=True)
    if path.parent != cache or path.name != f"download-{asset.digest}.exe":
        raise UpdateError("Invalid cached installer path.")
    helper_source = safe_path(root / "NeckerUpdater.exe", file=True)
    with cache_lock(cache):
        if path.stat().st_size != asset.size or hash_file(path, cancel) != asset.digest:
            raise UpdateError("The cached installer changed. Download it again.")
        digest = hash_file(helper_source, cancel)
        helper = safe_path(cache / f"helper-{digest}.exe", file=True)
        if not helper.exists():
            with helper.open("xb") as destination, helper_source.open("rb") as source:
                while chunk := source.read(1024**2):
                    destination.write(chunk)
        if hash_file(helper, cancel) != digest:
            raise UpdateError("The staged update helper failed verification.")
    check_cancel(cancel)
    process = subprocess.Popen([str(helper), str(os.getpid()), str(root), current_version(app),
                                asset.version, str(path), asset.digest, str(asset.size)],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                               text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    # Helper initialization is bounded. No installer runs without the ACCEPT message.
    from queue import Queue, Empty
    import threading
    messages = Queue()
    threading.Thread(target=lambda: messages.put(process.stdout.readline()), daemon=True).start()
    try:
        deadline = time.monotonic() + 30
        while True:
            check_cancel(cancel)
            try:
                line = messages.get(timeout=.1)
                break
            except Empty:
                if time.monotonic() > deadline:
                    raise UpdateError("The update helper did not respond.")
        if line.strip() != "READY":
            raise UpdateError("The update helper could not prepare installation.")
        check_cancel(cancel)
        process.stdin.write("ACCEPT\n")
        process.stdin.flush()
        # No cancellation after acceptance: the helper now owns installation.
        threading.Thread(target=lambda: messages.put(process.stdout.readline()), daemon=True).start()
        try:
            if messages.get(timeout=30).strip() != "ACCEPTED":
                raise UpdateError("The update helper did not accept installation.")
        except Empty:
            raise UpdateError("The update helper did not acknowledge installation.") from None
        process.stdin.close()
        return process
    except BaseException:
        process.stdin.close()
        raise
    finally:
        process.stdout.close()
