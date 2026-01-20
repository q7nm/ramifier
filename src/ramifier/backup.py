import shutil
import tarfile
from pathlib import Path

import zstandard as zstd

from .log import log_info, log_warning
from .state import get_hash_history, get_last_backup, mark_backup, mark_hash
from .target import Target
from .utils import current_timestamp, ensure_dir, get_tree_state_hash


def backup_target(target: Target, force: bool = False):
    current_hash = get_tree_state_hash(target.path)

    if not force and not _has_changes(target, current_hash):
        log_info("Nothing to backup", target.name)
        mark_hash(target, current_hash)
        return

    backup_file = target.backup_path / f"{target.name}-{current_timestamp()}.tar.zst"
    _compress_target(target, backup_file)
    mark_backup(target, backup_file)
    mark_hash(target, current_hash)
    _cleanup_old_backups(target)


def restore_target(target: Target):
    backup_file = Path(get_last_backup(target))
    if not backup_file.exists():
        raise FileNotFoundError(f"Backup file not found")

    _decompress_target(target, backup_file)


def _has_changes(target: Target, current_hash: str) -> bool:
    last_hash = (get_hash_history(target) or [None])[-1]
    return current_hash != last_hash


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
