"""Signed blockchain transactions."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from typing import Any

from blockchain.serialization import canonical_dumps, now_ms
from config import ALGORITHM_ECDSA, ALGORITHM_MLDSA, MIN_AMOUNT, SUPPORTED_ALGORITHMS
from crypto.crypto_factory import CryptoFactory
from crypto.crypto_utils import decode_bytes, encode_bytes


@dataclass
class Transaction:
    transaction_id: str
    sender: str
    receiver: str
    amount: float
    timestamp: float
    algorithm: str
    public_key: str
    signature: str
    nonce: str = ""

    def create_message(self) -> str:
        return canonical_dumps(
            {
                "sender": self.sender,
                "receiver": self.receiver,
                "amount": self.amount,
                "timestamp": self.timestamp,
                "transaction_id": self.transaction_id,
            }
        )

    def calculate_transaction_id(self) -> str:
        payload = canonical_dumps(
            {
                "sender": self.sender,
                "receiver": self.receiver,
                "amount": self.amount,
                "timestamp": self.timestamp,
                "nonce": self.nonce,
            }
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "algorithm": self.algorithm,
            "public_key": self.public_key,
            "signature": self.signature,
            "nonce": self.nonce,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Transaction:
        return cls(
            transaction_id=str(data.get("transaction_id", "")),
            sender=str(data.get("sender", "")),
            receiver=str(data.get("receiver", "")),
            amount=round(float(data.get("amount", 0)), 8),
            timestamp=int(float(data.get("timestamp", 0))),
            algorithm=str(data.get("algorithm", "")),
            public_key=str(data.get("public_key", "")),
            signature=str(data.get("signature", "")),
            nonce=str(data.get("nonce", "")),
        )

    def is_valid(self) -> tuple[bool, str]:
        if not self.sender or not str(self.sender).strip():
            return False, "missing sender"
        if not self.receiver or not str(self.receiver).strip():
            return False, "missing receiver"
        if self.sender.strip() == self.receiver.strip():
            return False, "sender and receiver must differ"
        try:
            amount = float(self.amount)
        except (TypeError, ValueError):
            return False, "invalid amount"
        if amount <= 0 or amount < MIN_AMOUNT:
            return False, "invalid amount"
        if self.timestamp <= 0:
            return False, "invalid timestamp"
        if self.algorithm not in SUPPORTED_ALGORITHMS:
            return False, "unsupported algorithm"
        if not self.signature:
            return False, "missing signature"
        if not self.public_key:
            return False, "missing public key"
        if not self.nonce:
            return False, "missing nonce"
        expected_id = self.calculate_transaction_id()
        if self.transaction_id != expected_id:
            return False, "inconsistent transaction ID"
        try:
            public_key = decode_bytes(self.public_key)
            signature = decode_bytes(self.signature)
        except (ValueError, TypeError):
            return False, "malformed encoded key or signature"
        message = self.create_message().encode("utf-8")
        try:
            wallet = CryptoFactory.create_verifier(self.algorithm)
            ok = wallet.verify(message, signature, public_key)
        except Exception:
            return False, "malformed signature or public key"
        if not ok:
            return False, "invalid signature"
        return True, "valid"

    @classmethod
    def create_signed(
        cls,
        sender: str,
        receiver: str,
        amount: float,
        algorithm: str,
        wallet,
        timestamp: float | None = None,
        nonce: str | None = None,
    ) -> Transaction:
        if timestamp is None:
            timestamp = now_ms()
        if nonce is None:
            nonce = uuid.uuid4().hex
        tx = cls(
            transaction_id="",
            sender=sender,
            receiver=receiver,
            amount=round(float(amount), 8),
            timestamp=int(timestamp),
            algorithm=algorithm,
            public_key=encode_bytes(wallet.get_public_key_bytes()),
            signature="",
            nonce=nonce,
        )
        tx.transaction_id = tx.calculate_transaction_id()
        message = tx.create_message().encode("utf-8")
        tx.signature = encode_bytes(wallet.sign(message))
        return tx


def algorithm_display(name: str) -> str:
    if name == ALGORITHM_MLDSA:
        return "ML-DSA-44"
    if name == ALGORITHM_ECDSA:
        return "ECDSA"
    return name
