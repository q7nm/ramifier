import shutil
import tarfile
from pathlib import Path

import zstandard as zstd

from .global_settings import GlobalSettings
from .log import log_info, log_warning
from .state import (
    get_last_backup,
    get_last_hash,
    get_mtime_history,
    mark_backup,
    mark_hash,
    mark_mtime,
)
from .target import Target
from .utils import current_timestamp, ensure_dir, hash_file_list


def backup_target(target: Target, force: bool = False):
    current_mtime = max(
        (p.stat().st_mtime for p in target.path.rglob("*") if p.is_file()), default=0.0
    )
    current_hash = hash_file_list(target.path)

    if not force and not _has_changes(target, current_mtime, current_hash):
        log_info("Nothing to backup", target.name)
        if not force:
            mark_mtime(target, current_mtime)
        return

    backup_file = target.backup_path / f"{target.name}-{current_timestamp()}.tar.zst"
    _compress_target(target, backup_file)
    mark_backup(target, backup_file)
    mark_mtime(target, current_mtime)
    mark_hash(target, current_hash)
    _cleanup_old_backups(target)


def restore_target(target: Target):
    backup_file = Path(get_last_backup(target))
    if not backup_file.exists():
        raise FileNotFoundError(f"No backup found for target {target.name}")

    _decompress_target(target, backup_file)
    log_info("Restored from backup", target.name)


def _has_changes(target: Target, current_mtime: float, current_hash: str) -> bool:
    last_mtime = (get_mtime_history(target) or [0.0])[-1]
    last_hash = get_last_hash(target)
    return current_mtime > last_mtime or current_hash != last_hash


def _compress_target(target: Target, backup_file: Path):
    cctx = zstd.ZstdCompressor(
        level=target.compression_level, threads=target.compression_threads
    )

    with open(backup_file, "wb") as f_out:
        with cctx.stream_writer(f_out) as compressor:
            with tarfile.open(fileobj=compressor, mode="w|") as tar:
                tar.add(target.path.resolve(), arcname=".")
    log_info(f"Backed up at {backup_file}", target.name)


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
    backups = sorted(
        target.backup_path.glob(f"{target.name}-*.tar.zst"),
        key=lambda p: p.stat().st_mtime,
    )
    last_backup_file = get_last_backup(target)

    for backup in backups[: -target.max_backups]:
        try:
            if last_backup_file is None or backup != Path(last_backup_file):
                backup.unlink(missing_ok=True)
                log_info(f"Deleted old backup: {backup}", target.name)
        except Exception:
            log_warning(f"Failed to delete {backup}", target.name)
