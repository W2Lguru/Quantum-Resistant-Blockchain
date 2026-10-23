"""Create wallets without exposing algorithm internals to the blockchain."""

from __future__ import annotations

from config import ALGORITHM_ECDSA, ALGORITHM_MLDSA
from crypto.base_wallet import BaseWallet
from crypto.ecdsa_wallet import ECDSAWallet
from crypto.mldsa_wallet import MLDSAWallet


def _normalize(algorithm: str) -> str:
    return algorithm.strip().upper().replace("_", "-")


class CryptoFactory:
    @staticmethod
    def create_verifier(algorithm: str) -> BaseWallet:
        name = _normalize(algorithm)
        if name in {ALGORITHM_ECDSA, "ECDSA-SECP256K1"}:
            return ECDSAWallet()
        if name in {ALGORITHM_MLDSA, "ML-DSA-44", "MLDSA", "MLDSA-44"}:
            return MLDSAWallet()
        raise ValueError(f"unsupported algorithm: {algorithm}")

    @staticmethod
    def create_wallet(algorithm: str) -> BaseWallet:
        wallet = CryptoFactory.create_verifier(algorithm)
        wallet.generate_keys()
        return wallet

    @staticmethod
    def restore_wallet(algorithm: str, public_key: bytes, secret_key: bytes) -> BaseWallet:
        name = algorithm.strip().upper().replace("_", "-")
        if name in {ALGORITHM_ECDSA, "ECDSA-SECP256K1"}:
            return ECDSAWallet.from_secret_material(secret_key)
        if name in {ALGORITHM_MLDSA, "ML-DSA-44", "MLDSA", "MLDSA-44"}:
            return MLDSAWallet.from_persisted(public_key, secret_key)
        raise ValueError(f"unsupported algorithm: {algorithm}")
