"""Session helpers used by the Streamlit UI. Cryptography stays in backend modules."""

from __future__ import annotations

from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction, algorithm_display
from config import BLOCKCHAIN_PATH, DEFAULT_VALIDATOR
from crypto.crypto_factory import CryptoFactory
from security.wallet_store import ProtectedWalletStore


def load_or_create_chain() -> Blockchain:
    if not BLOCKCHAIN_PATH.exists():
        chain = Blockchain()
        chain.save_to_file(BLOCKCHAIN_PATH)
        return chain
    try:
        return Blockchain.load_from_file(BLOCKCHAIN_PATH)
    except (ValueError, OSError, KeyError, TypeError):
        # Do not overwrite a saved chain that failed to load.
        return Blockchain()


def commit_pending_block(chain: Blockchain, validator: str = DEFAULT_VALIDATOR) -> dict:
    if not chain.pending_transactions:
        return {"added": False, "reason": "no pending transactions", "block_index": None}
    block = chain.create_block(validator)
    added, reason = chain.add_block(block)
    if added:
        chain.save_to_file(BLOCKCHAIN_PATH)
    return {"added": added, "reason": reason, "block_index": block.index if added else None}


def create_and_commit_transaction(
    chain: Blockchain,
    sender: str,
    receiver: str,
    amount: float,
    algorithm: str,
    wallet=None,
    validator: str = DEFAULT_VALIDATOR,
    auto_mine: bool = True,
) -> dict:
    if wallet is None:
        wallet = CryptoFactory.create_wallet(algorithm)
    tx = Transaction.create_signed(sender, receiver, amount, algorithm, wallet)
    accepted, reason = chain.add_transaction(tx)
    result = {
        "accepted": accepted,
        "reason": reason,
        "transaction": tx.to_dict(),
        "algorithm_display": algorithm_display(algorithm),
        "signature_size": len(bytes.fromhex(tx.signature)) if tx.signature else 0,
        "public_key_size": len(bytes.fromhex(tx.public_key)) if tx.public_key else 0,
        "valid": tx.is_valid()[0],
        "block_added": False,
    }
    if accepted and auto_mine:
        block = chain.create_block(validator)
        added, block_reason = chain.add_block(block)
        result["block_added"] = added
        result["block_reason"] = block_reason
        result["block_index"] = block.index if added else None
        if added:
            chain.save_to_file(BLOCKCHAIN_PATH)
    return result


def wallet_store() -> ProtectedWalletStore:
    return ProtectedWalletStore()
