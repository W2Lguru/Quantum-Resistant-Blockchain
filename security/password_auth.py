"""Password hashing with scrypt. Never store or print plaintext passwords."""

from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass

from config import (
    PASSWORD_DKLEN,
    PASSWORD_SALT_BYTES,
    PASSWORD_SCRYPT_N,
    PASSWORD_SCRYPT_P,
    PASSWORD_SCRYPT_R,
)


@dataclass
class PasswordRecord:
    salt_hex: str
    hash_hex: str


def hash_password(password: str, salt: bytes | None = None) -> PasswordRecord:
    if not password:
        raise ValueError("password must not be empty")
    salt = salt or os.urandom(PASSWORD_SALT_BYTES)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=PASSWORD_SCRYPT_N,
        r=PASSWORD_SCRYPT_R,
        p=PASSWORD_SCRYPT_P,
        dklen=PASSWORD_DKLEN,
    )
    return PasswordRecord(salt_hex=salt.hex(), hash_hex=digest.hex())


def verify_password(password: str, record: PasswordRecord) -> bool:
    try:
        salt = bytes.fromhex(record.salt_hex)
        digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=PASSWORD_SCRYPT_N,
            r=PASSWORD_SCRYPT_R,
            p=PASSWORD_SCRYPT_P,
            dklen=PASSWORD_DKLEN,
        )
        return hmac.compare_digest(digest.hex(), record.hash_hex)
    except Exception:
        return False


def derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=PASSWORD_SCRYPT_N,
        r=PASSWORD_SCRYPT_R,
        p=PASSWORD_SCRYPT_P,
        dklen=32,
    )
