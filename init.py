#!/usr/bin/env python3
"""Install the portable Codex configuration bundle into a Codex home.

The installer only manages the top-level preference values represented by the
bundled config template. Existing project trust settings, comments, and other
configuration are retained.
"""

from __future__ import annotations

import argparse
import datetime as _datetime
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
import tomllib
import uuid


_TARGET_KEYS = (
    "model",
    "model_reasoning_effort",
    "approval_policy",
    "sandbox_mode",
    "service_tier",
)
_ASSIGNMENT_RE = re.compile(
    r"^(?P<prefix>[ \t]*(?P<key>model|model_reasoning_effort|approval_policy|"
    r"sandbox_mode|service_tier)[ \t]*=[ \t]*)(?P<rest>.*)$"
)


class SetupError(RuntimeError):
    """An expected setup or validation error."""


def _source_path(name: str) -> Path:
    bundle_dir = Path(__file__).resolve().parent
    path = bundle_dir / name
    if path.is_symlink():
        raise SetupError(f"bundled source must not be a symlink: {path}")
    if not path.is_file():
        raise SetupError(f"bundled source is missing: {path}")
    return path


def _read_source(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise SetupError(f"cannot read bundled source {path}: {exc}") from exc


def _decode_utf8(data: bytes, label: str) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SetupError(f"{label} is not valid UTF-8: {exc}") from exc


def _parse_config(text: str, label: str) -> dict:
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise SetupError(f"invalid TOML in {label}: {exc}") from exc


def _template_settings(text: str, label: str) -> dict[str, str]:
    parsed = _parse_config(text, label)
    if set(parsed) != set(_TARGET_KEYS):
        raise SetupError(
            f"{label} must contain exactly the managed top-level settings"
        )
    settings: dict[str, str] = {}
    for key in _TARGET_KEYS:
        value = parsed[key]
        if not isinstance(value, str):
            raise SetupError(f"{label} has non-string {key}={value!r}")
        settings[key] = value
    return settings


def _validate_settings(text: str, label: str, settings: dict[str, str]) -> dict:
    parsed = _parse_config(text, label)
    for key, expected in settings.items():
        if parsed.get(key) != expected:
            actual = parsed.get(key, "<missing>")
            raise SetupError(
                f"{label} has {key}={actual!r}; expected {expected!r}"
            )
    return parsed


def _split_inline_comment(value: str) -> tuple[str, str]:
    """Return the value and suffix, keeping comments and trailing whitespace."""

    in_basic = False
    in_literal = False
    escaped = False
    comment_at: int | None = None
    for index, char in enumerate(value):
        if in_basic:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_basic = False
        elif in_literal:
            if char == "'":
                in_literal = False
        elif char == '"':
            in_basic = True
        elif char == "'":
            in_literal = True
        elif char == "#":
            comment_at = index
            break

    if comment_at is None:
        value_part = value
        comment = ""
    else:
        value_part = value[:comment_at]
        comment = value[comment_at:]

    value_end = len(value_part.rstrip(" \t"))
    return value_part[:value_end], value_part[value_end:] + comment


def _is_table_header(line: str) -> bool:
    stripped = line.lstrip(" \t")
    return stripped.startswith("[")


def _replace_top_level_settings(text: str, settings: dict[str, str]) -> str:
    """Replace only the managed assignments before the first TOML table."""

    lines = text.splitlines(keepends=True)
    replaced: set[str] = set()
    output: list[str] = []
    in_table = False

    for line in lines:
        newline = ""
        body = line
        if line.endswith("\r\n"):
            body, newline = line[:-2], "\r\n"
        elif line.endswith(("\n", "\r")):
            body, newline = line[:-1], line[-1]

        stripped = body.lstrip(" \t")
        if stripped and not stripped.startswith("#") and _is_table_header(body):
            in_table = True

        match = None if in_table else _ASSIGNMENT_RE.match(body)
        if match:
            key = match.group("key")
            _, suffix = _split_inline_comment(match.group("rest"))
            output.append(
                match.group("prefix") + '"' + settings[key] + '"' + suffix + newline
            )
            replaced.add(key)
        else:
            output.append(line)

    missing = [key for key in _TARGET_KEYS if key not in replaced]
    if not missing:
        return "".join(output)

    insertion_index = len(output)
    for index, line in enumerate(output):
        if _is_table_header(line):
            insertion_index = index
            break

    before = "".join(output[:insertion_index])
    after = "".join(output[insertion_index:])
    if before and not before.endswith(("\n", "\r")):
        before += "\n"
    inserted = "".join(
        f'{key} = "{settings[key]}"\n' for key in missing
    )
    return before + inserted + after


def _validate_target_file(path: Path) -> None:
    if path.is_symlink():
        raise SetupError(f"refusing to modify symlink target: {path}")
    if path.exists() and not path.is_file():
        raise SetupError(f"target exists but is not a regular file: {path}")


def _unique_backup_path(path: Path) -> Path:
    stamp = _datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    while True:
        candidate = path.with_name(f"{path.name}.bak-{stamp}-{uuid.uuid4().hex[:12]}")
        if not candidate.exists() and not candidate.is_symlink():
            return candidate


def _atomic_write(path: Path, data: bytes) -> None:
    mode = None
    if path.exists():
        mode = stat.S_IMODE(path.stat().st_mode)

    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    temporary = Path(temporary_name)
    try:
        if mode is not None:
            os.chmod(temporary, mode)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _backup(path: Path, backup_path: Path) -> None:
    try:
        shutil.copy2(path, backup_path)
    except OSError as exc:
        raise SetupError(f"cannot back up {path} to {backup_path}: {exc}") from exc


def _target_from_args(args: argparse.Namespace) -> Path:
    if args.codex_home is not None:
        return args.codex_home.expanduser()
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".codex"


def _prepare(args: argparse.Namespace) -> tuple[Path, list[tuple[Path, bytes, Path | None]], list[Path]]:
    source_config = _source_path("config.toml")
    source_agents = _source_path("AGENTS.md")
    config_text = _decode_utf8(_read_source(source_config), str(source_config))
    settings = _template_settings(config_text, str(source_config))
    _validate_settings(config_text, str(source_config), settings)
    agents_data = _read_source(source_agents)
    agents_text = _decode_utf8(agents_data, str(source_agents))
    if not agents_text.strip():
        raise SetupError(f"bundled instructions are empty: {source_agents}")

    target = _target_from_args(args)
    if target.exists() and not target.is_dir():
        raise SetupError(f"Codex home exists but is not a directory: {target}")
    if target.is_symlink():
        raise SetupError(f"refusing symlink Codex home: {target}")

    config_path = target / "config.toml"
    agents_path = target / "AGENTS.md"
    _validate_target_file(config_path)
    _validate_target_file(agents_path)

    if config_path.exists():
        existing_config_data = _read_source(config_path)
        existing_config_text = _decode_utf8(existing_config_data, str(config_path))
        existing_config = _parse_config(existing_config_text, str(config_path))
        resulting_config_text = _replace_top_level_settings(existing_config_text, settings)
    else:
        existing_config_data = None
        existing_config = None
        resulting_config_text = config_text
    resulting_config = _validate_settings(
        resulting_config_text, f"resulting {config_path}", settings
    )
    if existing_config is not None:
        existing_other = {
            key: value
            for key, value in existing_config.items()
            if key not in settings
        }
        resulting_other = {
            key: value
            for key, value in resulting_config.items()
            if key not in settings
        }
        if existing_other != resulting_other:
            raise SetupError(
                f"managed update changed unrelated TOML data in {config_path}"
            )
    resulting_config_data = resulting_config_text.encode("utf-8")

    existing_agents_data = _read_source(agents_path) if agents_path.exists() else None
    config_changed = existing_config_data != resulting_config_data
    agents_changed = existing_agents_data != agents_data
    operations: list[tuple[Path, bytes, Path | None]] = []
    if config_changed:
        operations.append(
            (
                config_path,
                resulting_config_data,
                _unique_backup_path(config_path) if existing_config_data is not None else None,
            )
        )
    if agents_changed:
        operations.append(
            (
                agents_path,
                agents_data,
                _unique_backup_path(agents_path) if existing_agents_data is not None else None,
            )
        )
    return target, operations, [source_config, source_agents]


def _apply(target: Path, operations: list[tuple[Path, bytes, Path | None]], dry_run: bool) -> None:
    if not operations:
        print(f"No changes needed in {target}")
        return

    for path, _, backup_path in operations:
        if backup_path is not None:
            print(f"Back up {path} -> {backup_path}")
        print(f"Write {path}")

    if dry_run:
        print("Dry run: no files changed.")
        return

    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise SetupError(f"cannot create Codex home {target}: {exc}") from exc

    for path, data, backup_path in operations:
        if backup_path is not None:
            _backup(path, backup_path)
        try:
            _atomic_write(path, data)
        except OSError as exc:
            raise SetupError(f"cannot write {path}: {exc}") from exc
    print(f"Installed portable setup in {target}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--codex-home",
        type=Path,
        help="destination Codex home (default: CODEX_HOME or ~/.codex)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show planned changes without creating backups or writing files",
    )
    args = parser.parse_args(argv)

    try:
        target, operations, _ = _prepare(args)
        _apply(target, operations, args.dry_run)
    except SetupError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
