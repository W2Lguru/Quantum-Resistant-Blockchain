"""Educational Proof-of-Authority blockchain with JSON persistence."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from blockchain.block import Block
from blockchain.serialization import now_ms
from blockchain.transaction import Transaction
from blockchain.validator import BlockValidator
from config import (
    BLOCKCHAIN_PATH,
    DEFAULT_VALIDATOR,
    GENESIS_INDEX,
    GENESIS_PREVIOUS_HASH,
    GENESIS_VALIDATOR,
    INITIAL_BALANCES,
    VALIDATORS,
)


class Blockchain:
    def __init__(self, validators: tuple[str, ...] = VALIDATORS) -> None:
        self.chain: list[Block] = []
        self.pending_transactions: list[Transaction] = []
        self.validators = list(validators)
        self.seen_transaction_ids: set[str] = set()
        self.spent_nonces: set[tuple[str, str]] = set()
        self.balances: dict[str, float] = defaultdict(float, INITIAL_BALANCES)
        self.validator_engine = BlockValidator(tuple(self.validators))
        self.create_genesis_block()

    def create_genesis_block(self) -> Block:
        genesis = Block(
            index=GENESIS_INDEX,
            timestamp=now_ms(),
            transactions=[],
            previous_hash=GENESIS_PREVIOUS_HASH,
            validator=GENESIS_VALIDATOR,
        )
        genesis.hash = genesis.calculate_hash()
        self.chain = [genesis]
        self.pending_transactions = []
        self.seen_transaction_ids = set()
        self.spent_nonces = set()
        self.balances = defaultdict(float, INITIAL_BALANCES)
        return genesis

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def get_balance(self, account: str) -> float:
        reserved = sum(tx.amount for tx in self.pending_transactions if tx.sender == account)
        return float(self.balances.get(account, 0.0) - reserved)

    def add_transaction(self, transaction: Transaction) -> tuple[bool, str]:
        ok, reason = transaction.is_valid()
        if not ok:
            return False, reason
        if transaction.transaction_id in self.seen_transaction_ids:
            return False, "replay detected: transaction ID already used"
        if (transaction.sender, transaction.nonce) in self.spent_nonces:
            return False, "replay detected: nonce already used"
        if any(p.transaction_id == transaction.transaction_id for p in self.pending_transactions):
            return False, "replay detected: duplicate pending transaction"
        available = self.get_balance(transaction.sender)
        if transaction.amount > available:
            return False, "double-spend or insufficient balance (simulation)"
        self.pending_transactions.append(transaction)
        return True, "accepted"

    def create_block(self, validator: str = DEFAULT_VALIDATOR) -> Block:
        latest = self.get_latest_block()
        block = Block(
            index=latest.index + 1,
            timestamp=now_ms(),
            transactions=list(self.pending_transactions),
            previous_hash=latest.hash,
            validator=validator,
        )
        block.hash = block.calculate_hash()
        return block

    def add_block(self, block: Block) -> tuple[bool, str]:
        ok, reason = self.validate_block(block)
        if not ok:
            return False, reason
        for tx in block.transactions:
            if tx.transaction_id in self.seen_transaction_ids:
                return False, "replay detected during block commit"
            available = float(self.balances.get(tx.sender, 0.0))
            if tx.amount > available:
                return False, "double-spend or insufficient balance (simulation)"
            self.balances[tx.sender] = available - tx.amount
            self.balances[tx.receiver] = float(self.balances.get(tx.receiver, 0.0)) + tx.amount
            self.seen_transaction_ids.add(tx.transaction_id)
            self.spent_nonces.add((tx.sender, tx.nonce))
        committed_ids = {tx.transaction_id for tx in block.transactions}
        self.pending_transactions = [
            tx for tx in self.pending_transactions if tx.transaction_id not in committed_ids
        ]
        self.chain.append(block)
        return True, "block added"

    def validate_block(self, block: Block) -> tuple[bool, str]:
        if not self.chain:
            return self.validator_engine.validate_block(block, None)
        if block.index == 0:
            return self.validator_engine.validate_block(block, None)
        previous = self.get_latest_block()
        return self.validator_engine.validate_block(block, previous)

    def is_chain_valid(self) -> tuple[bool, str]:
        if not self.chain:
            return False, "empty chain"
        for i, block in enumerate(self.chain):
            previous = self.chain[i - 1] if i > 0 else None
            ok, reason = self.validator_engine.validate_block(block, previous)
            if not ok:
                return False, f"block {block.index}: {reason}"
        return True, "valid"

    def get_transaction_history(self) -> list[dict[str, Any]]:
        history = []
        for block in self.chain:
            for tx in block.transactions:
                item = tx.to_dict()
                item["block_index"] = block.index
                history.append(item)
        return history

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions],
            "validators": self.validators,
            "balances": dict(self.balances),
            "seen_transaction_ids": sorted(self.seen_transaction_ids),
            "spent_nonces": [[sender, nonce] for sender, nonce in sorted(self.spent_nonces)],
        }

    def save_to_file(self, path: Path | None = None) -> Path:
        target = Path(path or BLOCKCHAIN_PATH)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return target

    @classmethod
    def load_from_file(cls, path: Path | None = None) -> Blockchain:
        target = Path(path or BLOCKCHAIN_PATH)
        chain = cls()
        if not target.exists():
            chain.save_to_file(target)
            return chain
        try:
            raw = json.loads(target.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"corrupted blockchain JSON: {exc}") from exc
        if not isinstance(raw, dict) or "chain" not in raw:
            raise ValueError("malformed blockchain data")
        loaded = cls()
        loaded.validators = list(raw.get("validators") or VALIDATORS)
        loaded.validator_engine = BlockValidator(tuple(loaded.validators))
        loaded.chain = [Block.from_dict(item) for item in raw["chain"]]
        loaded.pending_transactions = [
            Transaction.from_dict(item) for item in raw.get("pending_transactions", [])
        ]
        loaded.balances = defaultdict(float, raw.get("balances") or INITIAL_BALANCES)
        loaded.seen_transaction_ids = set(raw.get("seen_transaction_ids", []))
        loaded.spent_nonces = {
            (str(item[0]), str(item[1])) for item in raw.get("spent_nonces", [])
        }
        if not loaded.chain:
            raise ValueError("malformed blockchain data: empty chain")
        ok, reason = loaded.is_chain_valid()
        if not ok:
            raise ValueError(f"refusing to load invalid chain: {reason}")
        return loaded
