"""Proof-of-Authority style block validation."""

from __future__ import annotations

from blockchain.block import Block
from config import GENESIS_INDEX, GENESIS_PREVIOUS_HASH, GENESIS_VALIDATOR, VALIDATORS


class BlockValidator:
    def __init__(self, authorized_validators: tuple[str, ...] = VALIDATORS) -> None:
        self.authorized_validators = set(authorized_validators)

    def validate_block(self, block: Block, previous: Block | None) -> tuple[bool, str]:
        if previous is None:
            if block.index != GENESIS_INDEX:
                return False, "incorrect genesis index"
            if block.previous_hash != GENESIS_PREVIOUS_HASH:
                return False, "incorrect genesis previous hash"
            if block.validator != GENESIS_VALIDATOR:
                return False, "incorrect genesis validator"
            if block.transactions:
                return False, "genesis must have no transactions"
        else:
            if block.index != previous.index + 1:
                return False, "incorrect index"
            if block.previous_hash != previous.hash:
                return False, "previous hash mismatch"
            if block.validator not in self.authorized_validators:
                return False, "unauthorized validator"
            for tx in block.transactions:
                ok, reason = tx.is_valid()
                if not ok:
                    return False, f"invalid transaction: {reason}"
        recalculated = block.calculate_hash()
        if block.hash != recalculated:
            return False, "hash mismatch"
        return True, "valid"
