#!/usr/bin/env python3
"""Manage standalone supercoding copies; native plugins use their host's updater (Python 3.9+)."""

import argparse
from contextlib import contextmanager
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import uuid
import zipfile

sys.dont_write_bytecode = True
import validate_skill as validator

REPOSITORY = "Cyrus-terra/supercoding"
FILES = {"SKILL.md", *(f"references/{name}" for name in validator.REFERENCES)}
MAX_FILE = 2 * 1024 * 1024
MAX_ARCHIVE = 20 * 1024 * 1024
MAX_EXPANDED = 64 * 1024 * 1024
CLIENT_PATHS = {
    "claude": ".claude", "codebuddy": ".codebuddy", "codex": ".agents",
    "gemini": ".gemini", "hermes": ".hermes", "openclaw": ".openclaw",
}


def version_key(value):
    if not isinstance(value, str) or not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", value):
        raise ValueError(f"unsupported stable version: {value!r}; expected x.y.z")
    return tuple(map(int, value.split(".")))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_payload(payload):
    if set(payload) != FILES:
        raise ValueError("source must contain exactly SKILL.md and the eight runtime references")
    texts = {}
    for name, data in payload.items():
        if len(data) > MAX_FILE:
            raise ValueError(f"runtime file exceeds limit: {name}")
        texts[name] = data.decode("utf-8")
    errors = []
    _, _, metadata = validator.parse_entry(texts["SKILL.md"], Path("SKILL.md"), Path("supercoding"), errors)
    for name, text in texts.items():
        for raw in validator.LINK.findall(text):
            link = urlsplit(raw.strip().strip("<>"))
            if link.scheme or link.netloc or not link.path:
                continue
            path = PurePosixPath(name).parent / unquote(link.path)
            parts = []
            for part in path.parts:
                if part == "..":
                    if not parts:
                        errors.append(f"link escapes Skill: {name}: {raw}")
                        break
                    parts.pop()
                elif part not in ("", "."):
                    parts.append(part)
            else:
                if "/".join(parts) not in FILES:
                    errors.append(f"missing linked runtime file: {name}: {raw}")
    if errors:
        raise ValueError("invalid source: " + "; ".join(errors))
    version = metadata["version"]
    version_key(version)
    return version


def no_links(path):
    # Require canonical OS paths as well; /var and /tmp are symlink aliases on macOS.
    for item in (path, *path.parents):
        if item.is_symlink():
            raise ValueError(f"symlink path refused: {item}; update the source explicitly instead")


def inventory(root):
    result = {}
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"expected a real Skill directory: {root}")
    for directory, directories, filenames in os.walk(root, followlinks=False):
        for name in directories + filenames:
            path = Path(directory) / name
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                raise ValueError(f"links and special files are not supported: {path}")
        for name in filenames:
            path = Path(directory) / name
            if path.stat().st_size > MAX_FILE:
                raise ValueError(f"file exceeds management limit: {path}")
            result[path.relative_to(root).as_posix()] = digest(path.read_bytes())
        if len(result) > 128:
            raise ValueError("too many files in standalone target")
    return result


def installed_version(target):
    entry = target / "SKILL.md"
    if not entry.is_file() or entry.stat().st_size > MAX_FILE:
        raise ValueError(f"target is not an identifiable supercoding Skill: {target}")
    errors = []
    _, fields, metadata = validator.parse_entry(entry.read_text(encoding="utf-8"), Path("SKILL.md"), Path("supercoding"), errors)
    # Local rule edits may break links/formatting. Preserve them on explicit replacement.
    if fields.get("name") != "supercoding":
        raise ValueError("refusing to replace a directory that is not named supercoding in its entry")
    value = metadata.get("version", "")
    version_key(value)
    return value


def local_bundle(raw):
    root = Path(os.path.abspath(Path(raw).expanduser()))
    no_links(root)
    if not (root / "SKILL.md").is_file():
        root = root / "skills/supercoding"
    actual = inventory(root)
    actual.pop(".DS_Store", None)  # Finder metadata is not part of a runtime release.
    if set(actual) != FILES:
        raise ValueError("local source must contain exactly the nine runtime files")
    payload = {name: (root / name).read_bytes() for name in FILES}
    version = validate_payload(payload)
    return {"files": payload, "version": version, "source": str(root), "commit": None}


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, url):
        check_url(url)
        return super().redirect_request(request, fp, code, message, headers, url)


def check_url(url):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in {"api.github.com", "github.com", "codeload.github.com"} or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError("unexpected release URL; only the fixed GitHub HTTPS origins are accepted")


def download(url, limit):
    check_url(url)
    request = Request(url, headers={"User-Agent": "supercoding-manager", "Accept": "application/vnd.github+json"})
    with build_opener(SafeRedirect()).open(request, timeout=15) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("release response exceeds size limit")
    return data


def api(path):
    result = json.loads(download(f"https://api.github.com/repos/{REPOSITORY}/{path}", 1024 * 1024))
    if not isinstance(result, dict):
        raise ValueError("invalid GitHub API response")
    return result


def archive_payload(data, commit):
    payload = {}
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = archive.infolist()
        if len(members) > 4096 or sum(item.file_size for item in members) > MAX_EXPANDED:
            raise ValueError("release archive exceeds member or expanded-size limit")
        seen = set()
        roots = set()
        for item in members:
            path = PurePosixPath(item.filename)
            mode = item.external_attr >> 16
            if path.is_absolute() or ".." in path.parts or "\\" in item.filename or item.filename in seen or stat.S_ISLNK(mode):
                raise ValueError("unsafe or duplicate release archive member")
            if not path.parts:
                raise ValueError("empty archive path")
            roots.add(path.parts[0])
            seen.add(item.filename)
            if len(path.parts) >= 4 and path.parts[1:3] == ("skills", "supercoding"):
                name = PurePosixPath(*path.parts[3:]).as_posix()
                if item.is_dir():
                    continue
                if name not in FILES or name in payload or item.file_size > MAX_FILE:
                    raise ValueError("unexpected runtime member in release")
                if stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                    raise ValueError("non-regular runtime member")
                payload[name] = archive.read(item)
        if len(roots) != 1 or not next(iter(roots)).endswith(commit):
            raise ValueError("archive root does not match resolved immutable commit")
    return payload


def remote_bundle(version=None):
    if version:
        version_key(version)
    try:
        release = api("releases/tags/" + quote("v" + version, safe="") if version else "releases/latest")
    except HTTPError as exc:
        if exc.code == 404:
            raise ValueError("no matching stable GitHub Release; publish a release or use --source <local-checkout>") from exc
        raise
    tag = release.get("tag_name", "")
    if release.get("draft") or release.get("prerelease") or not isinstance(tag, str) or not tag.startswith("v"):
        raise ValueError("a published stable vX.Y.Z Release is required")
    version_key(tag[1:])
    if version and tag != "v" + version:
        raise ValueError("requested version and release tag differ")
    commit = api("commits/" + quote(tag, safe="")).get("sha", "")
    if not isinstance(commit, str) or not re.fullmatch("[0-9a-f]{40}", commit):
        raise ValueError("release did not resolve to an immutable commit")
    data = download(f"https://codeload.github.com/{REPOSITORY}/zip/{commit}", MAX_ARCHIVE)
    payload = archive_payload(data, commit)
    actual = validate_payload(payload)
    if actual != tag[1:]:
        raise ValueError("release tag and Skill version differ")
    return {"files": payload, "version": actual, "source": f"{REPOSITORY}@{tag}", "commit": commit}


def source_bundle(args):
    return local_bundle(args.source) if args.source else remote_bundle(args.version)


def target_path(args):
    if args.target:
        target = Path(os.path.abspath(Path(args.target).expanduser()))
    else:
        target = Path.home() / CLIENT_PATHS[args.client] / "skills/supercoding"
    if target.name != "supercoding" or target.parent == target or target == Path.home() / "supercoding":
        raise ValueError("target must be a dedicated skills/supercoding directory, not a home or client root")
    no_links(target)
    # Do not replace a source checkout or a client-managed plugin tree.
    if (target / ".git").exists() or (target / "skills").exists() or (target / "plugin.json").exists():
        raise ValueError("target appears to be a repository or plugin; use the client's updater")
    return target


def state_root(target):
    return target.parent / ".supercoding-state"


def safe_state(target):
    state = state_root(target)
    no_links(state)
    if state.exists() and not state.is_dir():
        raise ValueError("management state is not a directory")
    return state


def read_json(path):
    if path.is_symlink():
        raise ValueError(f"symlink management file refused: {path}")
    if not path.exists():
        return None
    if path.stat().st_size > MAX_FILE:
        raise ValueError("management state exceeds size limit")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("invalid management state")
    return value


def write_json(path, value):
    no_links(path)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


@contextmanager
def locked(target):
    state = safe_state(target)
    state.mkdir(parents=True, exist_ok=True)
    lock = state / "lock"
    no_links(lock)
    with lock.open("a+b") as stream:
        if os.name == "nt":
            import msvcrt
            stream.seek(0)
            stream.write(b"0")
            stream.flush()
            stream.seek(0)
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise ValueError("another management operation holds the target lock") from exc
        else:
            import fcntl
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise ValueError("another management operation holds the target lock") from exc
        yield state


def inspection(target):
    state = safe_state(target)
    version = installed_version(target)
    actual = inventory(target)
    receipt = read_json(state / "receipt.json")
    managed = bool(receipt and receipt.get("target") == str(target) and receipt.get("files") == actual and receipt.get("version") == version)
    return version, actual, managed


def check_overlap(bundle, target):
    if bundle["commit"] is not None:
        return
    source = Path(bundle["source"])
    repo = source.parent.parent if source.parent.name == "skills" else source
    if validator.inside(repo, target) or validator.inside(target, source):
        raise ValueError("source and target overlap; choose an external standalone destination")


def receipt(bundle, target):
    return {"schema": 1, "target": str(target), "version": bundle["version"], "source": bundle["source"], "commit": bundle["commit"], "files": {name: digest(data) for name, data in bundle["files"].items()}}


def backup_path(state):
    return state / "backups" / (str(time.time_ns()) + "-" + uuid.uuid4().hex)


def switch(bundle, target, state):
    """Journaled two-rename replacement; process crashes may require rollback."""
    if read_json(state / "transaction.json"):
        raise ValueError("unfinished transaction: run rollback before another update")
    staging = state / ("stage-" + uuid.uuid4().hex)
    staging.mkdir()
    try:
        for name, data in bundle["files"].items():
            path = staging / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        if validate_payload({name: (staging / name).read_bytes() for name in FILES}) != bundle["version"]:
            raise ValueError("staged version differs")
        old_receipt = read_json(state / "receipt.json")
        old = None
        if target.exists():
            old = backup_path(state)
            old.parent.mkdir(parents=True, exist_ok=True)
            no_links(old.parent)
        transaction = {"target": str(target), "backup": old.name if old else None, "old_receipt": old_receipt, "old_files": inventory(target) if old else None, "stage": staging.name}
        write_json(state / "transaction.json", transaction)
        try:
            if old:
                target.rename(old)
            staging.rename(target)
            write_json(state / "receipt.json", receipt(bundle, target))
            if old:
                write_json(old.with_suffix(".json"), {"target": str(target), "files": transaction["old_files"], "receipt": old_receipt})
            (state / "transaction.json").unlink()
            return old
        except Exception:
            # Keep displaced new files for inspection; never discard the old installation.
            if old and old.exists():
                if target.exists():
                    target.rename(state / ("failed-" + uuid.uuid4().hex))
                old.rename(target)
            elif not old and target.exists():
                target.rename(state / ("failed-" + uuid.uuid4().hex))
            if old_receipt is not None:
                write_json(state / "receipt.json", old_receipt)
            elif (state / "receipt.json").exists():
                (state / "receipt.json").unlink()
            (state / "transaction.json").unlink()
            raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def show_change(bundle, target, actual):
    desired = {name: digest(data) for name, data in bundle["files"].items()}
    changed = sorted(name for name in set(desired) | set(actual) if desired.get(name) != actual.get(name))
    print(f"available: {bundle['version']} ({bundle['source']})")
    if bundle["commit"]:
        print(f"commit: {bundle['commit']}")
    print("changed files: " + (", ".join(changed) or "none"))
    return changed


def apply(args):
    target = target_path(args)
    bundle = source_bundle(args)
    check_overlap(bundle, target)
    if args.command == "check" or args.dry_run:
        version, actual, managed = inspection(target) if target.exists() else (None, {}, False)
        print(f"installed: {version or 'absent'}; managed and unchanged: {managed}")
        show_change(bundle, target, actual)
        return
    with locked(target) as state:
        no_links(target)
        if read_json(state / "transaction.json"):
            raise ValueError("unfinished transaction: run rollback before another update")
        if args.command == "install" and target.exists():
            raise ValueError("target already exists; compare with check and use update explicitly")
        if args.command == "update":
            current, actual, managed = inspection(target)
            if version_key(bundle["version"]) < version_key(current):
                raise ValueError("downgrades require explicit rollback")
            if not managed and not args.replace:
                raise ValueError("unmanaged or modified target; inspect with --dry-run, then use --replace to preserve it in a backup")
            if not show_change(bundle, target, actual) and managed:
                print("already current; nothing changed")
                return
        old = switch(bundle, target, state)
        print(f"installed {bundle['version']} at {target}")
        if old:
            print(f"backup: {old}")
        print("start a new client session to use the updated rules")


def restore(args):
    target = target_path(args)
    with locked(target) as state:
        journal = read_json(state / "transaction.json")
        if journal:
            if journal.get("target") != str(target):
                raise ValueError("transaction target mismatch")
            name = journal.get("backup")
            if not isinstance(name, str) or not re.fullmatch(r"\d+-[a-f0-9]{32}", name):
                raise ValueError("no prior installation in interrupted transaction; inspect state manually")
            backup = state / "backups" / name
            metadata = {"target": str(target), "files": journal.get("old_files"), "receipt": journal.get("old_receipt")}
        else:
            root = state / "backups"
            no_links(root)
            choices = sorted((p for p in root.iterdir() if re.fullmatch(r"\d+-[a-f0-9]{32}", p.name)), reverse=True) if root.exists() else []
            if not choices:
                raise ValueError("no backup available")
            backup = choices[0]
            metadata = read_json(backup.with_suffix(".json"))
        no_links(backup)
        if journal and not backup.exists() and target.exists() and inventory(target) == metadata.get("files"):
            # A previous rollback moved the backup successfully but stopped before receipt commit.
            previous = metadata.get("receipt")
            if previous is not None:
                write_json(state / "receipt.json", previous)
            elif (state / "receipt.json").exists():
                (state / "receipt.json").unlink()
            (state / "transaction.json").unlink()
            print(f"completed interrupted rollback at {target}")
            return
        if not metadata or metadata.get("target") != str(target) or inventory(backup) != metadata.get("files"):
            raise ValueError("backup metadata or contents differ; restore refused")
        installed_version(backup)
        displaced = None
        current_receipt = read_json(state / "receipt.json")
        if target.exists():
            installed_version(target)
            displaced = backup_path(state)
            write_json(displaced.with_suffix(".json"), {"target": str(target), "files": inventory(target), "receipt": current_receipt})
        # Persist recovery information before moving either installation.
        write_json(state / "transaction.json", {"target": str(target), "backup": backup.name, "old_files": metadata["files"], "old_receipt": metadata.get("receipt")})
        try:
            if displaced:
                target.rename(displaced)
            backup.rename(target)
            previous = metadata.get("receipt")
            if previous is not None:
                write_json(state / "receipt.json", previous)
            elif (state / "receipt.json").exists():
                (state / "receipt.json").unlink()
            (state / "transaction.json").unlink()
        except Exception:
            if not target.exists() and displaced and displaced.exists():
                displaced.rename(target)
            raise
        print(f"restored {installed_version(target)} at {target}; displaced version preserved: {displaced}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("install", "check", "update", "rollback"):
        child = sub.add_parser(command)
        destination = child.add_mutually_exclusive_group(required=True)
        destination.add_argument("--target", help="full standalone path ending in supercoding")
        destination.add_argument("--client", choices=CLIENT_PATHS, help="default home path only; use --target for custom profiles")
        if command != "rollback":
            source = child.add_mutually_exclusive_group()
            source.add_argument("--source", help="offline repository root or runtime directory; otherwise latest GitHub Release")
            source.add_argument("--version", help="specific published stable release, x.y.z")
            child.add_argument("--dry-run", action="store_true", help="read-only preview, including for install")
        if command == "update":
            child.add_argument("--replace", action="store_true", help="explicitly replace an unmanaged/modified copy, retaining a backup")
    args = parser.parse_args()
    try:
        restore(args) if args.command == "rollback" else apply(args)
        return 0
    except (OSError, ValueError, URLError, zipfile.BadZipFile, RuntimeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
