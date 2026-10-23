"""Deterministic JSON helpers for hashing and signatures."""

from __future__ import annotations

import json
import time
from typing import Any


def canonical_dumps(obj: Any) -> str:
    """Serialize *obj* with stable key order and no extra whitespace."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_dumps_bytes(obj: Any) -> bytes:
    return canonical_dumps(obj).encode("utf-8")


def now_ms() -> int:
    """Integer millisecond timestamp so hashes and signatures survive JSON save/load."""
    return time.time_ns() // 1_000_000
