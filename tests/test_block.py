"""Automated tests for Block creation, hashing, and serialization."""

from __future__ import annotations

from blockchain.block import Block
from blockchain.blockchain import Blockchain


def test_genesis_creation():
    chain = Blockchain()
    genesis = chain.chain[0]
    assert genesis.index == 0
    assert genesis.previous_hash == "0"
    assert genesis.validator == "GENESIS"
    assert genesis.transactions == []
    assert genesis.hash == genesis.calculate_hash()


def test_hash_excludes_hash_field():
    block = Block(1, 1.0, [], "abc", "Validator1", hash="deadbeef")
    assert "deadbeef" not in block.payload()
    assert block.calculate_hash() == Block(1, 1.0, [], "abc", "Validator1").calculate_hash()


def test_block_serialization_roundtrip():
    block = Block(1, 1000.0, [], "0" * 64, "Validator1")
    block.hash = block.calculate_hash()
    data = block.to_dict()
    restored = Block.from_dict(data)
    assert restored.index == block.index
    assert restored.timestamp == block.timestamp
    assert restored.previous_hash == block.previous_hash
    assert restored.validator == block.validator
    assert restored.hash == block.hash
    assert restored.calculate_hash() == block.calculate_hash()
