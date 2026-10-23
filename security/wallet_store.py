"""Encrypted wallet access layer. Private keys never leave encrypted storage unencrypted."""

from __future__ import annotations

import json
import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
import base64

from config import WALLET_DIR
from crypto.crypto_factory import CryptoFactory
from crypto.crypto_utils import encode_bytes
from security.password_auth import PasswordRecord, derive_key, hash_password, verify_password


def _fernet_from_password(password: str, salt: bytes) -> Fernet:
    raw = derive_key(password, salt)
    key = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=b"qrb-wallet").derive(raw)
    return Fernet(base64.urlsafe_b64encode(key))


class ProtectedWalletStore:
    def __init__(self, directory: Path | None = None) -> None:
        self.directory = Path(directory or WALLET_DIR)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.failed_attempts: dict[str, int] = {}

    def _path(self, name: str) -> Path:
        safe = "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_"))
        if not safe:
            raise ValueError("invalid wallet name")
        return self.directory / f"{safe}.wallet.json"

    def create(self, name: str, password: str, algorithm: str) -> dict:
        path = self._path(name)
        if path.exists():
            raise ValueError("wallet already exists")
        wallet = CryptoFactory.create_wallet(algorithm)
        record = hash_password(password)
        salt = bytes.fromhex(record.salt_hex)
        fernet = _fernet_from_password(password, salt)
        secret = wallet.export_secret_material()
        payload = {
            "name": name,
            "algorithm": wallet.get_algorithm_name(),
            "public_key": encode_bytes(wallet.get_public_key_bytes()),
            "kdf": "scrypt",
            "salt": record.salt_hex,
            "password_hash": record.hash_hex,
            "secret_blob": fernet.encrypt(secret).decode("ascii"),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return {
            "name": name,
            "algorithm": payload["algorithm"],
            "public_key": payload["public_key"],
            "public_key_size": len(wallet.get_public_key_bytes()),
        }

    def authenticate(self, name: str, password: str):
        path = self._path(name)
        if not path.exists():
            return False, "wallet not found", None
        if self.failed_attempts.get(name, 0) >= 5:
            return False, "too many failed logins", None
        data = json.loads(path.read_text(encoding="utf-8"))
        record = PasswordRecord(salt_hex=data["salt"], hash_hex=data["password_hash"])
        if not verify_password(password, record):
            self.failed_attempts[name] = self.failed_attempts.get(name, 0) + 1
            return False, "authentication failed", None
        self.failed_attempts[name] = 0
        try:
            fernet = _fernet_from_password(password, bytes.fromhex(data["salt"]))
            secret = fernet.decrypt(data["secret_blob"].encode("ascii"))
            public_key = bytes.fromhex(data["public_key"])
            wallet = CryptoFactory.restore_wallet(data["algorithm"], public_key, secret)
        except (InvalidToken, ValueError):
            return False, "unable to unlock wallet", None
        return True, "authenticated", wallet

    def list_wallets(self) -> list[str]:
        return sorted(p.stem.replace(".wallet", "") for p in self.directory.glob("*.wallet.json"))
