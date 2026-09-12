"""Temporary directories for the tests.

Deliberately **not** pytest's `tmp_path`. On the Windows host this project is
exercised on, `tempfile.mkdtemp` (which `tmp_path` uses underneath) produces a
directory with ACLs the process cannot write into afterwards, so every test that
asks for `tmp_path` fails with `PermissionError: [WinError 5]`.

A plain `mkdir` next to the tests works on Windows, Linux and macOS alike, so
the suite stays portable and does not need a platform branch.
"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

SCRATCH_ROOT = Path(__file__).resolve().parent / ".scratch"


def make_scratch() -> Path:
    SCRATCH_ROOT.mkdir(parents=True, exist_ok=True)
    target = SCRATCH_ROOT / f"t-{uuid.uuid4().hex[:10]}"
    target.mkdir()
    return target


def drop_scratch(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
