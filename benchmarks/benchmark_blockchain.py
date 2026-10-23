"""Measure serialized sizes of actual generated transactions and blocks."""

from __future__ import annotations

import json
import time
from typing import Any

from blockchain.blockchain import Blockchain
from blockchain.serialization import canonical_dumps
from blockchain.transaction import Transaction
from config import ALGORITHM_ECDSA, ALGORITHM_MLDSA, STORAGE_TX_COUNTS
from crypto.crypto_factory import CryptoFactory


def _measure_chain(algorithm: str, tx_count: int) -> dict[str, Any]:
    chain = Blockchain()
    wallet = CryptoFactory.create_wallet(algorithm)
    sender = "Alice"
    receiver = "Bob"
    chain.balances[sender] = float(tx_count) + 10.0
    sizes_tx = []
    sizes_pk = []
    sizes_sig = []
    for i in range(tx_count):
        tx = Transaction.create_signed(sender, receiver, 1.0, algorithm, wallet)
        sizes_tx.append(len(canonical_dumps(tx.to_dict()).encode("utf-8")))
        sizes_pk.append(len(bytes.fromhex(tx.public_key)))
        sizes_sig.append(len(bytes.fromhex(tx.signature)))
        ok, reason = chain.add_transaction(tx)
        if not ok:
            raise RuntimeError(f"transaction rejected during storage benchmark: {reason}")
        if len(chain.pending_transactions) >= 25:
            block = chain.create_block("Validator1")
            added, reason = chain.add_block(block)
            if not added:
                raise RuntimeError(reason)
    if chain.pending_transactions:
        block = chain.create_block("Validator1")
        added, reason = chain.add_block(block)
        if not added:
            raise RuntimeError(reason)
    serialized = json.dumps(chain.to_dict()).encode("utf-8")
    latest = chain.get_latest_block()
    block_size = len(canonical_dumps(latest.to_dict()).encode("utf-8"))
    return {
        "algorithm": algorithm,
        "operation": f"storage_{tx_count}",
        "iterations": tx_count,
        "average_time_ms": 0.0,
        "min_time_ms": 0.0,
        "max_time_ms": 0.0,
        "std_dev_ms": 0.0,
        "data_size_bytes": len(serialized),
        "serialized_transaction_size_avg": sum(sizes_tx) / len(sizes_tx),
        "public_key_size": sum(sizes_pk) / len(sizes_pk),
        "signature_size": sum(sizes_sig) / len(sizes_sig),
        "serialized_block_size": block_size,
        "total_blockchain_size": len(serialized),
        "transaction_count": tx_count,
        "timestamp": time.time(),
    }


def run_storage_benchmarks(tx_counts: tuple[int, ...] = STORAGE_TX_COUNTS) -> list[dict[str, Any]]:
    rows = []
    for algorithm in (ALGORITHM_ECDSA, ALGORITHM_MLDSA):
        for count in tx_counts:
            rows.append(_measure_chain(algorithm, count))
    return rows
