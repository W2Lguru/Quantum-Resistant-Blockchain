"""Run all educational security demonstrations."""

from __future__ import annotations

from security.block_tampering import (
    demonstrate_block_tampering,
    demonstrate_previous_hash_manipulation,
)
from security.double_spending import demonstrate_double_spending
from security.malformed_input import demonstrate_algorithm_mismatch, demonstrate_malformed_transactions
from security.replay_attack import demonstrate_replay_attack
from security.signature_forgery import demonstrate_signature_forgery
from security.transaction_tampering import demonstrate_transaction_tampering
from security.validator_attack import (
    demonstrate_invalid_block_injection,
    demonstrate_unauthorized_validator,
)


def run_all_demonstrations(algorithm: str = "ECDSA") -> list[dict]:
    return [
        demonstrate_transaction_tampering(algorithm),
        demonstrate_block_tampering(),
        demonstrate_previous_hash_manipulation(),
        demonstrate_signature_forgery(algorithm),
        demonstrate_replay_attack(algorithm),
        demonstrate_double_spending(algorithm),
        demonstrate_unauthorized_validator(),
        demonstrate_invalid_block_injection(),
        demonstrate_algorithm_mismatch(),
        demonstrate_malformed_transactions(),
    ]
