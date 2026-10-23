"""Replay a previously accepted transaction using the same transaction ID and nonce."""

from __future__ import annotations

from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction
from crypto.crypto_factory import CryptoFactory


def demonstrate_replay_attack(algorithm: str = "ECDSA") -> dict:
    chain = Blockchain()
    wallet = CryptoFactory.create_wallet(algorithm)
    tx = Transaction.create_signed("Alice", "Bob", 25.0, algorithm, wallet)
    first_ok, first_reason = chain.add_transaction(tx)
    block = chain.create_block("Validator1")
    chain.add_block(block)
    replay = Transaction.from_dict(tx.to_dict())
    second_ok, second_reason = chain.add_transaction(replay)
    return {
        "name": "replay attack",
        "first_accepted": first_ok,
        "first_reason": first_reason,
        "replay_accepted": second_ok,
        "replay_reason": second_reason,
        "detected": first_ok and (not second_ok),
        "headline": "REPLAY DETECTED" if not second_ok else "UNEXPECTED RESULT",
        "explanation": (
            "Each transaction has a deterministic ID and a unique nonce. The "
            "ledger records used IDs and (sender, nonce) pairs so a previously "
            "accepted transaction cannot be submitted again."
        ),
    }
