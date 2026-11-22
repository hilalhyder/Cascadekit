"""Small I/O helpers shared by the collectors and builders."""
import glob
import gzip
import json
import os


def open_text(path, mode="r"):
    """Open a text file, transparently gzipped if the name ends in .gz."""
    if "w" in mode or "a" in mode:
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
    if str(path).endswith(".gz"):
        return gzip.open(path, mode + "t", encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def read_jsonl(pattern, recursive=True):
    """Yield records from every JSONL(.gz) file matching ``pattern``, skipping broken lines
    (for example the last line of a file after a crash)."""
    for path in sorted(glob.glob(pattern, recursive=recursive)):
        with open_text(path, "r") as fh:
            for line in fh:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
