"""Attempt to impersonate a sender using a different wallet. Does not break the scheme."""

from __future__ import annotations

from blockchain.transaction import Transaction
from crypto.crypto_factory import CryptoFactory
from crypto.crypto_utils import encode_bytes


def demonstrate_signature_forgery(algorithm: str = "ECDSA") -> dict:
    legitimate = CryptoFactory.create_wallet(algorithm)
    attacker = CryptoFactory.create_wallet(algorithm)
    forged = Transaction.create_signed("Alice", "Bob", 50.0, algorithm, attacker)
    legitimate_pk = encode_bytes(legitimate.get_public_key_bytes())
    checked = Transaction.from_dict(forged.to_dict())
    checked.public_key = legitimate_pk
    ok, reason = checked.is_valid()
    return {
        "name": "signature forgery attempt",
        "valid": ok,
        "reason": reason,
        "detected": not ok,
        "headline": "FORGERY REJECTED" if not ok else "UNEXPECTED RESULT",
        "explanation": (
            "The attacker signed with their own private key. Verification against "
            "Alice's public key fails. This demonstration does not attempt to "
            "cryptographically break ECDSA or ML-DSA."
        ),
    }
