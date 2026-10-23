"""Change a signed transaction amount without updating the signature."""

from __future__ import annotations

from blockchain.transaction import Transaction
from crypto.crypto_factory import CryptoFactory


def demonstrate_transaction_tampering(algorithm: str = "ECDSA") -> dict:
    wallet = CryptoFactory.create_wallet(algorithm)
    original = Transaction.create_signed("Alice", "Bob", 100.0, algorithm, wallet)
    ok_before, reason_before = original.is_valid()

    tampered = Transaction.from_dict(original.to_dict())
    tampered.amount = 1000.0
    ok_after, reason_after = tampered.is_valid()

    detected = (not ok_after) and ok_before
    return {
        "name": "transaction tampering",
        "original": original.to_dict(),
        "tampered": tampered.to_dict(),
        "valid_before": ok_before,
        "reason_before": reason_before,
        "valid_after": ok_after,
        "reason_after": reason_after,
        "detected": detected,
        "headline": "TRANSACTION TAMPERING DETECTED" if detected else "UNEXPECTED RESULT",
        "explanation": (
            "The amount was changed after signing. The canonical message no longer "
            "matches the signature, so verification fails."
        ),
    }
