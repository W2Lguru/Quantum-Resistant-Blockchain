"""Modify a committed transaction without repairing hash links."""

from __future__ import annotations

from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction
from crypto.crypto_factory import CryptoFactory


def _seed_chain() -> Blockchain:
    chain = Blockchain()
    wallet = CryptoFactory.create_wallet("ECDSA")
    tx = Transaction.create_signed("Alice", "Bob", 10.0, "ECDSA", wallet)
    chain.add_transaction(tx)
    block = chain.create_block("Validator1")
    chain.add_block(block)
    return chain


def demonstrate_block_tampering() -> dict:
    chain = _seed_chain()
    ok_before, reason_before = chain.is_chain_valid()
    target = chain.chain[1]
    if not target.transactions:
        raise RuntimeError("expected a non-genesis block with transactions")
    target.transactions[0].amount = 9999.0
    ok_after, reason_after = chain.is_chain_valid()
    return {
        "name": "block tampering",
        "valid_before": ok_before,
        "reason_before": reason_before,
        "valid_after": ok_after,
        "reason_after": reason_after,
        "detected": ok_before and (not ok_after),
        "headline": "CHAIN INVALID — HASH LINKING BROKEN" if not ok_after else "UNEXPECTED RESULT",
        "explanation": (
            "Changing a historical transaction changes the block payload. The stored "
            "hash no longer matches, so chain validation fails. Later blocks that "
            "store the previous hash would also fail if hashes were recomputed "
            "selectively."
        ),
    }


def demonstrate_previous_hash_manipulation() -> dict:
    chain = _seed_chain()
    ok_before, reason_before = chain.is_chain_valid()
    chain.chain[1].previous_hash = "0" * 64
    ok_after, reason_after = chain.is_chain_valid()
    return {
        "name": "previous-hash manipulation",
        "valid_before": ok_before,
        "reason_before": reason_before,
        "valid_after": ok_after,
        "reason_after": reason_after,
        "detected": ok_before and (not ok_after),
        "headline": "PREVIOUS-HASH MISMATCH DETECTED" if not ok_after else "UNEXPECTED RESULT",
        "explanation": "Blocks are linked by previous_hash. Changing it breaks the chain.",
    }
