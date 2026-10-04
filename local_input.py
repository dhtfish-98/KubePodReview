"""Read only a bounded, regular local file through one descriptor."""

from __future__ import annotations
import os
from pathlib import Path
import stat


def read_local_file(path: Path, limit: int = 4 * 1024 * 1024) -> bytes:
    path = Path(path)
    if path.is_symlink():
        raise ValueError("symbolic-link input is not accepted")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(path, flags)
    try:
        stream = os.fdopen(descriptor, "rb")
    except BaseException:
        os.close(descriptor)
        raise
    with stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("input must be a regular file")
        if info.st_size > limit:
            raise ValueError("input exceeds the byte limit")
        data = stream.read(limit + 1)
        if len(data) > limit:
            raise ValueError("input exceeds the byte limit")
        return data
