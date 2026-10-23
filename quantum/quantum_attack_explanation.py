"""Conceptual distinction between ECDSA threat model and ML-DSA design goals."""

from __future__ import annotations

ECDSA_PATH = [
    "ECDSA",
    "Elliptic-curve discrete logarithm problem",
    "Threatened by a sufficiently capable Shor algorithm",
]

MLDSA_PATH = [
    "ML-DSA",
    "Lattice-based cryptography",
    "Designed as a post-quantum signature scheme",
]

EXPLANATION = {
    "classical": (
        "Current blockchain systems commonly authenticate transactions with "
        "classical public-key signatures such as ECDSA. The security of ECDSA "
        "is related to the difficulty of the elliptic-curve discrete logarithm "
        "problem."
    ),
    "threat": (
        "A sufficiently capable fault-tolerant quantum computer could use "
        "Shor's algorithm to threaten cryptographic schemes based on discrete "
        "logarithms or integer factorization. This is a future cryptographic "
        "risk, not a claim that Bitcoin or secp256k1 has been broken today."
    ),
    "approach": (
        "ML-DSA (the NIST-standardized Dilithium family) is a lattice-based "
        "digital signature. It is designed to resist known quantum attacks that "
        "threaten classical public-key schemes such as those based on discrete "
        "logarithms. That is a design goal from post-quantum cryptography "
        "literature, not an absolute guarantee against every future attack."
    ),
    "demo_scope": (
        "The Qiskit module is an educational toy demonstration of order finding "
        "for N = 15. It does not break real cryptographic keys."
    ),
}


def narrative() -> dict:
    return {
        "ecdsa_path": ECDSA_PATH,
        "mldsa_path": MLDSA_PATH,
        "explanation": EXPLANATION,
    }
