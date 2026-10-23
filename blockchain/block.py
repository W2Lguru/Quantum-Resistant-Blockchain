"""SHA-256 hashed block for the educational PoA chain."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from blockchain.serialization import canonical_dumps
from blockchain.transaction import Transaction


@dataclass
class Block:
    index: int
    timestamp: float | int
    transactions: list[Transaction]
    previous_hash: str
    validator: str
    hash: str = ""

    def __post_init__(self) -> None:
        try:
            self.timestamp = int(self.timestamp)
        except (ValueError, TypeError):
            pass

    def payload(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "validator": self.validator,
        }

    def calculate_hash(self) -> str:
        digest = hashlib.sha256(canonical_dumps(self.payload()).encode("utf-8"))
        return digest.hexdigest()

    def to_dict(self) -> dict[str, Any]:
        data = self.payload()
        data["hash"] = self.hash
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Block:
        txs = [Transaction.from_dict(item) for item in data.get("transactions", [])]
        return cls(
            index=int(data["index"]),
            timestamp=int(float(data["timestamp"])),
            transactions=txs,
            previous_hash=str(data["previous_hash"]),
            validator=str(data["validator"]),
            hash=str(data.get("hash", "")),
        )
