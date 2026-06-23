from __future__ import annotations

import re
from pathlib import Path

TOKEN_LIKE_PATTERN = re.compile(r"\bTH[A-Za-z0-9_=-]{24,}\b")
HEX_SECRET_PATTERN = re.compile(r"\b[a-f0-9]{32,}\b", re.IGNORECASE)
ALLOWLIST = {"tests/test_no_plaintext_secrets.py"}


def iter_text_files() -> list[Path]:
    root = Path(__file__).resolve().parents[1]
    ignored_parts = {".git", ".venv", "dist", "build", ".pytest_cache", ".ruff_cache"}
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in ignored_parts for part in path.parts):
            continue
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        files.append(path)
    return files


def test_no_threads_tokens_or_hex_secrets_are_committed():
    root = Path(__file__).resolve().parents[1]
    offenders: list[str] = []
    for path in iter_text_files():
        rel = path.relative_to(root).as_posix()
        if rel in ALLOWLIST:
            continue
        text = path.read_text(encoding="utf-8")
        if TOKEN_LIKE_PATTERN.search(text) or HEX_SECRET_PATTERN.search(text):
            offenders.append(rel)
    assert offenders == []
