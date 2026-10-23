"""Safe rejection of malformed transactions and algorithm mismatch."""

from __future__ import annotations

import copy

from blockchain.transaction import Transaction
from crypto.crypto_factory import CryptoFactory


def demonstrate_algorithm_mismatch() -> dict:
    ecdsa = CryptoFactory.create_wallet("ECDSA")
    tx = Transaction.create_signed("Alice", "Bob", 7.0, "ECDSA", ecdsa)
    mismatched = Transaction.from_dict(tx.to_dict())
    mismatched.algorithm = "ML-DSA"
    ok, reason = mismatched.is_valid()
    return {
        "name": "algorithm mismatch",
        "accepted": ok,
        "reason": reason,
        "detected": not ok,
        "headline": "ALGORITHM MISMATCH REJECTED" if not ok else "UNEXPECTED RESULT",
        "explanation": (
            "Metadata claimed ML-DSA, but the public key and signature were produced "
            "by ECDSA. Verification fails safely."
        ),
    }


def demonstrate_malformed_transactions() -> dict:
    wallet = CryptoFactory.create_wallet("ECDSA")
    valid = Transaction.create_signed("Alice", "Bob", 3.0, "ECDSA", wallet)
    cases = []

    def check(label: str, mutate) -> None:
        data = copy.deepcopy(valid.to_dict())
        mutate(data)
        try:
            candidate = Transaction.from_dict(data)
            ok, reason = candidate.is_valid()
        except Exception as exc:
            ok, reason = False, f"rejected safely: {type(exc).__name__}"
        cases.append({"case": label, "accepted": ok, "reason": reason})

    check("negative amount", lambda d: d.update(amount=-1))
    check("zero amount", lambda d: d.update(amount=0))
    check("missing sender", lambda d: d.update(sender=""))
    check("missing receiver", lambda d: d.update(receiver=""))
    check("missing signature", lambda d: d.update(signature=""))
    check("missing public key", lambda d: d.update(public_key=""))
    check("invalid timestamp", lambda d: d.update(timestamp=-5))
    check("malformed signature", lambda d: d.update(signature="zz"))
    check("unsupported algorithm", lambda d: d.update(algorithm="RSA"))
    all_rejected = all(not item["accepted"] for item in cases)
    return {
        "name": "malformed transaction",
        "cases": cases,
        "detected": all_rejected,
        "headline": "MALFORMED INPUTS REJECTED" if all_rejected else "UNEXPECTED RESULT",
        "explanation": "Invalid amounts, missing fields, and malformed encodings are rejected without crashing.",
    }
