"""Unauthorized validator and invalid block injection demonstrations."""

from __future__ import annotations

from blockchain.block import Block
from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction
from crypto.crypto_factory import CryptoFactory


def demonstrate_unauthorized_validator() -> dict:
    chain = Blockchain()
    wallet = CryptoFactory.create_wallet("ECDSA")
    tx = Transaction.create_signed("Alice", "Bob", 5.0, "ECDSA", wallet)
    chain.add_transaction(tx)
    block = chain.create_block("AttackerValidator")
    ok, reason = chain.add_block(block)
    return {
        "name": "unauthorized validator",
        "validator": block.validator,
        "accepted": ok,
        "reason": reason,
        "detected": not ok,
        "headline": "UNAUTHORIZED VALIDATOR REJECTED" if not ok else "UNEXPECTED RESULT",
        "explanation": "Only Validator1, Validator2, and Validator3 may commit blocks.",
    }


def demonstrate_invalid_block_injection() -> dict:
    chain = Blockchain()
    bogus = Block(
        index=99,
        timestamp=1.0,
        transactions=[],
        previous_hash="deadbeef",
        validator="Validator1",
    )
    bogus.hash = bogus.calculate_hash()
    ok, reason = chain.add_block(bogus)
    return {
        "name": "invalid block injection",
        "accepted": ok,
        "reason": reason,
        "detected": not ok,
        "headline": "INVALID BLOCK REJECTED" if not ok else "UNEXPECTED RESULT",
        "explanation": "The injected block is incorrectly linked and has the wrong index.",
    }
