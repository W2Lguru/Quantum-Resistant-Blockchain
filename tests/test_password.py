from pathlib import Path

from security.password_auth import hash_password, verify_password
from security.wallet_store import ProtectedWalletStore


def test_password_hash_not_plaintext():
    record = hash_password("correct-horse")
    assert record.hash_hex != "correct-horse"
    assert verify_password("correct-horse", record)
    assert not verify_password("wrong", record)


def test_wallet_auth(tmp_path: Path):
    store = ProtectedWalletStore(tmp_path)
    meta = store.create("alice", "secret-pass", "ECDSA")
    assert "secret" not in meta
    ok, reason, wallet = store.authenticate("alice", "wrong")
    assert not ok
    ok, reason, wallet = store.authenticate("alice", "secret-pass")
    assert ok, reason
    assert wallet.get_public_key_size() > 0
    dumped = (tmp_path / "alice.wallet.json").read_text(encoding="utf-8")
    assert "BEGIN" not in dumped
    assert "private_key" not in dumped
