"""Educational hash-locked transfer contract for the prototype.

This is not an Ethereum-style smart-contract platform. It is a small,
explainable academic module: a signed transaction may carry a contract
payload that the chain evaluates before accepting a release of funds.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any

from blockchain.serialization import canonical_dumps


SUPPORTED_CONTRACTS = ("HASH_LOCK_TRANSFER",)


@dataclass
class HashLockTransfer:
    """Release funds only if a preimage matching a SHA-256 lock is provided."""

    contract_id: str
    sender: str
    receiver: str
    amount: float
    lock_hash: str
    created_at: float
    expires_at: float
    status: str = "LOCKED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "HASH_LOCK_TRANSFER",
            "contract_id": self.contract_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "lock_hash": self.lock_hash,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HashLockTransfer:
        return cls(
            contract_id=str(data["contract_id"]),
            sender=str(data["sender"]),
            receiver=str(data["receiver"]),
            amount=float(data["amount"]),
            lock_hash=str(data["lock_hash"]),
            created_at=float(data["created_at"]),
            expires_at=float(data["expires_at"]),
            status=str(data.get("status", "LOCKED")),
        )


def hash_preimage(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def create_hash_lock(
    sender: str,
    receiver: str,
    amount: float,
    secret: str,
    ttl_seconds: float = 3600.0,
) -> HashLockTransfer:
    now = time.time()
    lock_hash = hash_preimage(secret)
    payload = canonical_dumps(
        {
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "lock_hash": lock_hash,
            "created_at": now,
        }
    )
    contract_id = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return HashLockTransfer(
        contract_id=contract_id,
        sender=sender,
        receiver=receiver,
        amount=amount,
        lock_hash=lock_hash,
        created_at=now,
        expires_at=now + ttl_seconds,
    )


def execute_hash_lock(
    contract: HashLockTransfer,
    provided_secret: str,
    now: float | None = None,
) -> tuple[bool, str, HashLockTransfer]:
    """Evaluate contract conditions. Never logs the secret."""

    current = now if now is not None else time.time()
    updated = HashLockTransfer.from_dict(contract.to_dict())
    if updated.status != "LOCKED":
        return False, "contract is not in LOCKED state", updated
    if current > updated.expires_at:
        updated.status = "EXPIRED"
        return False, "contract expired", updated
    if hash_preimage(provided_secret) != updated.lock_hash:
        return False, "preimage does not match lock hash", updated
    updated.status = "RELEASED"
    return True, "hash lock satisfied; funds may be released", updated
