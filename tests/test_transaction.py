"""Automated tests for Transaction validation, signing, and serialization."""

from __future__ import annotations

import pytest

from blockchain.smart_contract import create_hash_lock, execute_hash_lock
from blockchain.transaction import Transaction
from crypto.crypto_factory import CryptoFactory


@pytest.mark.parametrize("algorithm", ["ECDSA", "ML-DSA"])
def test_valid_transaction(algorithm: str):
    wallet = CryptoFactory.create_wallet(algorithm)
    tx = Transaction.create_signed("Alice", "Bob", 10.0, algorithm, wallet)
    ok, reason = tx.is_valid()
    assert ok, reason
    assert tx.algorithm == algorithm
    assert tx.amount == 10.0
    assert tx.sender == "Alice"
    assert tx.receiver == "Bob"
    assert len(tx.signature) > 0
    assert len(tx.public_key) > 0


def test_invalid_amount():
    wallet = CryptoFactory.create_wallet("ECDSA")
    tx = Transaction.create_signed("Alice", "Bob", 1.0, "ECDSA", wallet)
    tx.amount = -5.0
    ok, reason = tx.is_valid()
    assert not ok
    assert "amount" in reason.lower()

    tx.amount = 0.0
    ok, reason = tx.is_valid()
    assert not ok
    assert "amount" in reason.lower()


def test_transaction_id_consistency():
    wallet = CryptoFactory.create_wallet("ECDSA")
    tx = Transaction.create_signed("Alice", "Bob", 2.0, "ECDSA", wallet)
    assert tx.transaction_id == tx.calculate_transaction_id()
    # Modifying nonce invalidates the transaction ID match
    tx.nonce = "tampered-nonce"
    ok, reason = tx.is_valid()
    assert not ok
    assert "transaction id" in reason.lower()


@pytest.mark.parametrize("algorithm", ["ECDSA", "ML-DSA"])
def test_serialization_roundtrip(algorithm: str):
    wallet = CryptoFactory.create_wallet(algorithm)
    tx = Transaction.create_signed("Alice", "Bob", 3.0, algorithm, wallet)
    restored = Transaction.from_dict(tx.to_dict())
    assert restored.to_dict() == tx.to_dict()
    assert restored.is_valid()[0] is True


def test_malformed_transaction():
    wallet = CryptoFactory.create_wallet("ECDSA")
    tx = Transaction.create_signed("Alice", "Bob", 4.0, "ECDSA", wallet)
    tx.signature = "not-hex"
    ok, reason = tx.is_valid()
    assert not ok

    # Missing fields
    tx2 = Transaction.from_dict(tx.to_dict())
    tx2.sender = ""
    ok, reason = tx2.is_valid()
    assert not ok
    assert "sender" in reason.lower()


def test_hash_lock_contract():
    contract = create_hash_lock("Alice", "Bob", 20.0, "demo-secret", ttl_seconds=60)
    ok, reason, updated = execute_hash_lock(contract, "wrong")
    assert not ok
    ok, reason, updated = execute_hash_lock(contract, "demo-secret")
    assert ok, reason
    assert updated.status == "RELEASED"
