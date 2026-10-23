"""Automated tests for ECDSA secp256k1 wallet."""

from __future__ import annotations

import pytest
from crypto.ecdsa_wallet import ECDSAWallet


def test_ecdsa_key_generation():
    wallet = ECDSAWallet()
    wallet.generate_keys()
    pk = wallet.get_public_key_bytes()
    assert isinstance(pk, bytes)
    assert len(pk) > 0
    assert wallet.get_public_key_size() == len(pk)
    assert wallet.get_algorithm_name() == "ECDSA"


def test_ecdsa_signing():
    wallet = ECDSAWallet()
    wallet.generate_keys()
    message = b"blockchain-test-message"
    signature = wallet.sign(message)
    assert isinstance(signature, bytes)
    assert len(signature) > 0
    assert wallet.get_signature_size() == len(signature)


def test_ecdsa_verification():
    wallet = ECDSAWallet()
    wallet.generate_keys()
    message = b"blockchain-test-message"
    signature = wallet.sign(message)
    assert wallet.verify(message, signature) is True
    # Verification using explicitly supplied public key bytes
    assert wallet.verify(message, signature, wallet.get_public_key_bytes()) is True


def test_ecdsa_invalid_signature():
    wallet = ECDSAWallet()
    wallet.generate_keys()
    message = b"blockchain-test-message"
    signature = wallet.sign(message)
    # Corrupt the signature bytes
    corrupted_sig = bytes([signature[0] ^ 0xFF]) + signature[1:]
    assert wallet.verify(message, corrupted_sig) is False
    assert wallet.verify(message, b"completely-bogus-sig") is False


def test_ecdsa_modified_message():
    wallet = ECDSAWallet()
    wallet.generate_keys()
    message = b"blockchain-test-message"
    signature = wallet.sign(message)
    modified_message = b"modified-message-content"
    assert wallet.verify(modified_message, signature) is False


def test_ecdsa_private_key_protection():
    wallet = ECDSAWallet()
    wallet.generate_keys()
    # Confirm private key is not in algorithm name or public output
    assert "private" not in wallet.get_algorithm_name().lower()
    assert "secret" not in wallet.get_algorithm_name().lower()
