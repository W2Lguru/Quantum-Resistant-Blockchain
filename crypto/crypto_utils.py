"""Shared encoding helpers. Never log private keys."""

from __future__ import annotations

import binascii


def encode_bytes(data: bytes) -> str:
    return binascii.hexlify(data).decode("ascii")


def decode_bytes(value: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise ValueError("empty encoding")
    return binascii.unhexlify(value.encode("ascii"))
