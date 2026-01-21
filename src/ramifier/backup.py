import os
import shutil
import tarfile
from pathlib import Path

import zstandard as zstd

from .log import log_info, log_warning
from .state import get_backups, get_hash_history, mark_backup, mark_hash, remove_backup
from .target import Target
from .utils import current_timestamp, ensure_dir, get_file_hash, get_tree_state_hash


def backup_target(target: Target, force: bool = False):
    current_hash = get_tree_state_hash(target.path)

    if not force and not _has_changes(target, current_hash):
        log_info("Nothing to backup", target.name)
        mark_hash(target, current_hash)
        return

    backup_file = target.backup_path / f"{target.name}-{current_timestamp()}.tar.zst"
    backup_hash = _compress_target(target, backup_file)
    mark_backup(target, backup_file, backup_hash)
    mark_hash(target, current_hash)
    _cleanup_old_backups(target)


def restore_target(target: Target):
    backups = get_backups(target)
    for backup in reversed(backups):
        file = backup.get("file")
        expected_hash = backup.get("hash")

        if not file or not expected_hash:
            continue

        backup_file = Path(file)
        if not backup_file.exists():
            log_warning(f"Backup file not found: {backup_file}", target.name)
            continue

        if expected_hash == get_file_hash(backup_file):
            _decompress_target(target, backup_file)
            return
        else:
            log_warning(f"Skipping backup (hash mismatch): {backup_file}", target.name)

    raise FileNotFoundError(f"No valid backup found")


def _has_changes(target: Target, current_hash: str) -> bool:
    last_hash = (get_hash_history(target) or [None])[-1]
    return current_hash != last_hash


def _compress_target(target: Target, backup_file: Path) -> str:
    cctx = zstd.ZstdCompressor(
        level=target.compression_level, threads=target.compression_threads
    )

    backup_temp_file = backup_file.with_suffix(backup_file.suffix + ".tmp")
    try:
        with open(backup_temp_file, "wb") as f_out:
            with cctx.stream_writer(f_out) as compressor:
                with tarfile.open(fileobj=compressor, mode="w|") as tar:
                    tar.add(target.path.resolve(), arcname=".")

        backup_hash = get_file_hash(backup_temp_file)
        os.replace(backup_temp_file, backup_file)
        log_info(f"Backed up at {backup_file}", target.name)
        return backup_hash

    finally:
        backup_temp_file.unlink(missing_ok=True)


def _decompress_target(target: Target, backup_file: Path):
    if target.path.exists():
        shutil.rmtree(target.path)
    ensure_dir(target.path)

    dctx = zstd.ZstdDecompressor()

    with open(backup_file, "rb") as f_in:
        with dctx.stream_reader(f_in) as decompressor:
            with tarfile.open(fileobj=decompressor, mode="r|") as tar:
                tar.extractall(target.path)
    log_info(f"Restored from {backup_file}", target.name)


def _cleanup_old_backups(target: Target):
    backups = get_backups(target)
    if not backups or len(backups) <= target.max_backups:
        return

    old_backups = backups[: -target.max_backups]
    for backup in old_backups:
        file = backup.get("file")
        if not file:
            continue

        backup_file = Path(file)
        try:
            if backup_file.exists():
                backup_file.unlink()
                log_info(f"Deleted old backup: {backup_file}", target.name)

        except Exception:
            log_warning(f"Failed to delete {backup_file}", target.name)

        finally:
            remove_backup(target, backup)
