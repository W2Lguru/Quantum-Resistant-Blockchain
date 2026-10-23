from pathlib import Path

from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction
from crypto.crypto_factory import CryptoFactory


def _signed(chain: Blockchain, amount: float = 5.0) -> Transaction:
    wallet = CryptoFactory.create_wallet("ECDSA")
    return Transaction.create_signed("Alice", "Bob", amount, "ECDSA", wallet)


def test_block_creation_and_validation():
    chain = Blockchain()
    tx = _signed(chain)
    ok, _ = chain.add_transaction(tx)
    assert ok
    block = chain.create_block("Validator1")
    added, reason = chain.add_block(block)
    assert added, reason
    valid, reason = chain.is_chain_valid()
    assert valid, reason


def test_invalid_previous_hash():
    chain = Blockchain()
    chain.add_transaction(_signed(chain))
    block = chain.create_block("Validator1")
    block.previous_hash = "ff" * 32
    block.hash = block.calculate_hash()
    ok, reason = chain.add_block(block)
    assert not ok
    assert "previous" in reason.lower() or "hash" in reason.lower()


def test_modified_block_hash():
    chain = Blockchain()
    chain.add_transaction(_signed(chain))
    block = chain.create_block("Validator1")
    chain.add_block(block)
    chain.chain[1].hash = "00" * 32
    ok, _ = chain.is_chain_valid()
    assert not ok


def test_unauthorized_validator():
    chain = Blockchain()
    chain.add_transaction(_signed(chain))
    block = chain.create_block("AttackerValidator")
    ok, reason = chain.add_block(block)
    assert not ok
    assert "unauthorized" in reason.lower()


def test_persistence(tmp_path: Path):
    path = tmp_path / "chain.json"
    chain = Blockchain()
    chain.add_transaction(_signed(chain))
    chain.add_block(chain.create_block("Validator2"))
    chain.save_to_file(path)
    loaded = Blockchain.load_from_file(path)
    assert len(loaded.chain) == len(chain.chain)
    assert loaded.chain[-1].hash == chain.chain[-1].hash


def test_multiple_blocks_persist(tmp_path: Path):
    path = tmp_path / "chain.json"
    chain = Blockchain()
    for _ in range(3):
        assert chain.add_transaction(_signed(chain))[0]
        added, reason = chain.add_block(chain.create_block("Validator1"))
        assert added, reason
    assert chain.get_latest_block().index == 3
    chain.save_to_file(path)
    loaded = Blockchain.load_from_file(path)
    assert loaded.get_latest_block().index == 3
    assert loaded.add_transaction(_signed(loaded))[0]
    added, reason = loaded.add_block(loaded.create_block("Validator3"))
    assert added, reason
    assert loaded.get_latest_block().index == 4
