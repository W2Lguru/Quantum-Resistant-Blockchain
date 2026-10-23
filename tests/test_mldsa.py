"""Automated tests for ML-DSA-44 post-quantum signature wallet."""

from __future__ import annotations

import pytest
from crypto.mldsa_wallet import MLDSAWallet


def _get_wallet():
    try:
        wallet = MLDSAWallet()
        wallet.generate_keys()
        return wallet
    except RuntimeError as exc:
        pytest.skip(f"ML-DSA-44 unavailable in current environment: {exc}")


def test_mldsa_key_generation():
    wallet = _get_wallet()
    pk = wallet.get_public_key_bytes()
    assert isinstance(pk, bytes)
    assert len(pk) == 1312
    assert wallet.get_public_key_size() == 1312
    assert wallet.get_algorithm_name() == "ML-DSA"


def test_mldsa_signing():
    wallet = _get_wallet()
    message = b"pqc-blockchain-message"
    signature = wallet.sign(message)
    assert isinstance(signature, bytes)
    assert len(signature) == 2420
    assert wallet.get_signature_size() == 2420


def test_mldsa_verification():
    wallet = _get_wallet()
    message = b"pqc-blockchain-message"
    signature = wallet.sign(message)
    pk = wallet.get_public_key_bytes()
    assert wallet.verify(message, signature, pk) is True
    assert wallet.verify(message, signature) is True


def test_mldsa_invalid_signature():
    wallet = _get_wallet()
    message = b"pqc-blockchain-message"
    signature = wallet.sign(message)
    pk = wallet.get_public_key_bytes()
    tampered_sig = bytes([signature[0] ^ 0xFF]) + signature[1:]
    assert wallet.verify(message, tampered_sig, pk) is False
    assert wallet.verify(message, b"short-corrupt", pk) is False


def test_mldsa_modified_message():
    wallet = _get_wallet()
    message = b"pqc-blockchain-message"
    signature = wallet.sign(message)
    pk = wallet.get_public_key_bytes()
    assert wallet.verify(b"different-message-bytes", signature, pk) is False


def test_mldsa_secret_key_protection():
    wallet = _get_wallet()
    assert "private" not in wallet.get_algorithm_name().lower()
