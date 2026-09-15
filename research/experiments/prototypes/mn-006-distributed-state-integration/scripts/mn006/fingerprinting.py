"""Platform-independent canonical serialization and SHA-256 helpers."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from typing import Any


def _normalise(value: Any) -> Any:
    """Convert frozen data structures into deterministic JSON-compatible values."""
    if is_dataclass(value):
        return _normalise(asdict(value))
    if isinstance(value, dict):
        return {str(key): _normalise(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_normalise(item) for item in value]
    return value


def canonical_json_bytes(value: Any) -> bytes:
    """Return UTF-8, sorted-key JSON with LF and exactly one final newline."""
    rendered = json.dumps(
        _normalise(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return (rendered + "\n").encode("utf-8")


def canonical_text_bytes(text: str) -> bytes:
    """Normalise CRLF/CR to LF and retain exactly one final LF."""
    normalised = text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
    return (normalised + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json_sha256(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def canonical_text_sha256(text: str) -> str:
    return sha256_bytes(canonical_text_bytes(text))
