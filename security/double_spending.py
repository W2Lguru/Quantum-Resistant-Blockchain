"""Educational double-spend simulation against simulated account balances."""

from __future__ import annotations

from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction
from crypto.crypto_factory import CryptoFactory


def demonstrate_double_spending(algorithm: str = "ECDSA") -> dict:
    chain = Blockchain()
    wallet = CryptoFactory.create_wallet(algorithm)
    available = chain.get_balance("Alice")
    first = Transaction.create_signed("Alice", "Bob", available, algorithm, wallet)
    second = Transaction.create_signed("Alice", "Charlie", 1.0, algorithm, wallet)
    first_ok, first_reason = chain.add_transaction(first)
    second_ok, second_reason = chain.add_transaction(second)
    return {
        "name": "double spending simulation",
        "available_balance": available,
        "first_accepted": first_ok,
        "first_reason": first_reason,
        "second_accepted": second_ok,
        "second_reason": second_reason,
        "detected": first_ok and (not second_ok),
        "headline": "CONFLICTING SPEND REJECTED" if not second_ok else "UNEXPECTED RESULT",
        "explanation": (
            "This is a simulation, not a production cryptocurrency accounting "
            "system. After the first spend reserves Alice's simulated balance, "
            "the second conflicting transaction is rejected."
        ),
    }
