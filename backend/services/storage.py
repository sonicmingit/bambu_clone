"""Storage service helpers for persisting uploaded files."""
from __future__ import annotations

import hashlib
import os
import pathlib
import secrets
from datetime import datetime
from typing import BinaryIO, Iterable, Tuple

CHUNK_SIZE = 1024 * 1024  # 1 MiB


def _iter_file_chunks(source: BinaryIO, chunk_size: int = CHUNK_SIZE) -> Iterable[bytes]:
    """Yield chunks from a file-like object without altering its final pointer."""
    while True:
        chunk = source.read(chunk_size)
        if not chunk:
            break
        yield chunk


def compute_checksum(source: BinaryIO, algorithm: str) -> str:
    """Compute checksum using the provided hashing algorithm name."""
    hasher = hashlib.new(algorithm)
    try:
        # attempt to remember starting position if seekable
        start_pos = source.tell()
        source.seek(0)
    except (AttributeError, OSError):
        start_pos = None

    for chunk in _iter_file_chunks(source):
        hasher.update(chunk)

    if start_pos is not None:
        source.seek(start_pos)

    return hasher.hexdigest()


def compute_md5(source: BinaryIO) -> str:
    """Return the MD5 digest for the provided file-like object."""
    return compute_checksum(source, "md5")


def compute_sha256(source: BinaryIO) -> str:
    """Return the SHA256 digest for the provided file-like object."""
    return compute_checksum(source, "sha256")


def generate_storage_path(base_directory: os.PathLike[str] | str, filename: str) -> pathlib.Path:
    """Generate a unique storage path for the file inside the base directory."""
    base_path = pathlib.Path(base_directory)
    timestamp = datetime.utcnow().strftime("%Y/%m/%d")
    unique = secrets.token_hex(8)
    safe_name = pathlib.Path(filename).name
    relative_path = pathlib.Path(timestamp) / f"{unique}_{safe_name}"
    return base_path.joinpath(relative_path)


def save_file(source: BinaryIO, destination: os.PathLike[str] | str, filename: str | None = None) -> Tuple[pathlib.Path, int, str, str]:
    """Persist a file-like object to disk and return metadata.

    Returns a tuple consisting of the written path, file size, md5 and sha256 digests.
    """
    if filename is None:
        filename = getattr(source, "name", secrets.token_hex(4))

    destination_path = generate_storage_path(destination, filename)
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure we start reading from the beginning if possible
    try:
        source.seek(0)
    except (AttributeError, OSError):
        pass

    md5_hash = hashlib.md5()
    sha_hash = hashlib.sha256()
    total = 0

    with destination_path.open("wb") as target:
        for chunk in _iter_file_chunks(source):
            target.write(chunk)
            md5_hash.update(chunk)
            sha_hash.update(chunk)
            total += len(chunk)

    # reset source for caller if possible
    try:
        source.seek(0)
    except (AttributeError, OSError):
        pass

    return destination_path, total, md5_hash.hexdigest(), sha_hash.hexdigest()

__all__ = [
    "save_file",
    "compute_md5",
    "compute_sha256",
    "generate_storage_path",
]
