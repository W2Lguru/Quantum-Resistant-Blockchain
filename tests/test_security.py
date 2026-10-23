"""Automated tests for all blockchain, cryptographic, and system security attacks."""

from __future__ import annotations

import pytest

from security.block_tampering import (
    demonstrate_block_tampering,
    demonstrate_previous_hash_manipulation,
)
from security.double_spending import demonstrate_double_spending
from security.malformed_input import (
    demonstrate_algorithm_mismatch,
    demonstrate_malformed_transactions,
)
from security.replay_attack import demonstrate_replay_attack
from security.signature_forgery import demonstrate_signature_forgery
from security.transaction_tampering import demonstrate_transaction_tampering
from security.validator_attack import (
    demonstrate_invalid_block_injection,
    demonstrate_unauthorized_validator,
)


@pytest.mark.parametrize("algorithm", ["ECDSA", "ML-DSA"])
def test_transaction_tampering(algorithm: str):
    result = demonstrate_transaction_tampering(algorithm)
    assert result["detected"] is True
    assert result["valid_before"] is True
    assert result["valid_after"] is False
    assert "TAMPERING DETECTED" in result["headline"]


def test_block_tampering():
    result = demonstrate_block_tampering()
    assert result["detected"] is True
    assert result["valid_before"] is True
    assert result["valid_after"] is False
    assert "HASH LINKING BROKEN" in result["headline"]


def test_previous_hash_manipulation():
    result = demonstrate_previous_hash_manipulation()
    assert result["detected"] is True
    assert result["valid_before"] is True
    assert result["valid_after"] is False
    assert "MISMATCH DETECTED" in result["headline"]


@pytest.mark.parametrize("algorithm", ["ECDSA", "ML-DSA"])
def test_forgery(algorithm: str):
    result = demonstrate_signature_forgery(algorithm)
    assert result["detected"] is True
    assert result["valid"] is False
    assert "REJECTED" in result["headline"]


@pytest.mark.parametrize("algorithm", ["ECDSA", "ML-DSA"])
def test_replay(algorithm: str):
    result = demonstrate_replay_attack(algorithm)
    assert result["detected"] is True
    assert result["first_accepted"] is True
    assert result["replay_accepted"] is False
    assert "REPLAY DETECTED" in result["headline"]


@pytest.mark.parametrize("algorithm", ["ECDSA", "ML-DSA"])
def test_double_spending(algorithm: str):
    result = demonstrate_double_spending(algorithm)
    assert result["detected"] is True
    assert result["first_accepted"] is True
    assert result["second_accepted"] is False
    assert "REJECTED" in result["headline"]


def test_unauthorized_validator():
    result = demonstrate_unauthorized_validator()
    assert result["detected"] is True
    assert result["accepted"] is False
    assert "UNAUTHORIZED" in result["headline"]


def test_invalid_block_injection():
    result = demonstrate_invalid_block_injection()
    assert result["detected"] is True
    assert result["accepted"] is False
    assert "INVALID BLOCK REJECTED" in result["headline"]


def test_algorithm_mismatch():
    result = demonstrate_algorithm_mismatch()
    assert result["detected"] is True
    assert result["accepted"] is False
    assert "MISMATCH REJECTED" in result["headline"]


def test_malformed_transactions():
    result = demonstrate_malformed_transactions()
    assert result["detected"] is True
    assert all(not case["accepted"] for case in result["cases"])
    assert "MALFORMED INPUTS REJECTED" in result["headline"]
