"""ML-DSA-44 wallet using the installed liboqs-python API."""

from __future__ import annotations

import os
from pathlib import Path

from config import ALGORITHM_MLDSA, MLDSA_VARIANT, ROOT_DIR
from crypto.base_wallet import BaseWallet

def _prepare_native_search_path() -> None:
    candidates = [
        ROOT_DIR / "third_party" / "liboqs",
        Path.home() / "_oqs",
    ]
    for prefix in candidates:
        bin_dir = prefix / "bin"
        if not bin_dir.exists():
            continue
        if "OQS_INSTALL_PATH" not in os.environ:
            os.environ["OQS_INSTALL_PATH"] = str(prefix)
        os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(str(bin_dir))
        break


_prepare_native_search_path()


def _load_oqs():
    try:
        import oqs
    except SystemExit as exc:
        raise RuntimeError(
            "liboqs native library was not found. Install Open Quantum Safe liboqs "
            "and place oqs.dll in third_party/liboqs/bin or %USERPROFILE%/_oqs/bin. "
            f"Details: {exc}"
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"liboqs-python import failed: {exc}") from exc
    return oqs


class MLDSAWallet(BaseWallet):
    def __init__(self) -> None:
        self._oqs = _load_oqs()
        self._signer = None
        self._public_key: bytes | None = None
        self._last_signature_size = 0
        enabled = []
        if hasattr(self._oqs, "get_enabled_sig_mechanisms"):
            enabled = list(self._oqs.get_enabled_sig_mechanisms())
        if MLDSA_VARIANT not in enabled:
            raise RuntimeError(
                f"{MLDSA_VARIANT} is not enabled in liboqs. Enabled: {enabled}"
            )

    def generate_keys(self) -> None:
        self._signer = self._oqs.Signature(MLDSA_VARIANT)
        self._public_key = self._signer.generate_keypair()

    def sign(self, message: bytes) -> bytes:
        if self._signer is None:
            raise RuntimeError("wallet keys have not been generated")
        signature = self._signer.sign(message)
        self._last_signature_size = len(signature)
        return signature

    def verify(self, message: bytes, signature: bytes, public_key: bytes | None = None) -> bool:
        try:
            verifier = self._oqs.Signature(MLDSA_VARIANT)
            key = public_key if public_key is not None else self._public_key
            if key is None:
                return False
            return bool(verifier.verify(message, signature, key))
        except Exception:
            return False

    def get_public_key_bytes(self) -> bytes:
        if self._public_key is None:
            raise RuntimeError("wallet keys have not been generated")
        return self._public_key

    def get_algorithm_name(self) -> str:
        return ALGORITHM_MLDSA

    def get_signature_size(self) -> int:
        if self._last_signature_size:
            return self._last_signature_size
        if self._signer is not None:
            return int(self._signer.details["length_signature"])
        return 2420

    def get_public_key_size(self) -> int:
        return len(self.get_public_key_bytes())

    def export_secret_material(self) -> bytes:
        if self._signer is None:
            raise RuntimeError("wallet keys have not been generated")
        return bytes(self._signer.export_secret_key())

    @classmethod
    def from_secret_material(cls, material: bytes) -> MLDSAWallet:
        wallet = cls()
        wallet._signer = wallet._oqs.Signature(MLDSA_VARIANT, secret_key=material)
        # Public key is not reconstructed from secret by this wrapper; generate a
        # matching public key by creating a throwaway pair is incorrect. Store
        # public||secret in encrypted material instead.
        raise RuntimeError("use from_persisted instead")

    @classmethod
    def from_persisted(cls, public_key: bytes, secret_key: bytes) -> MLDSAWallet:
        wallet = cls()
        wallet._signer = wallet._oqs.Signature(MLDSA_VARIANT, secret_key=secret_key)
        wallet._public_key = public_key
        return wallet
