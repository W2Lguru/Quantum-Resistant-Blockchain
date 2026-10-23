"""ECDSA secp256k1 wallet using the cryptography package."""

from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from config import ALGORITHM_ECDSA
from crypto.base_wallet import BaseWallet


class ECDSAWallet(BaseWallet):
    def __init__(self) -> None:
        self._private_key: ec.EllipticCurvePrivateKey | None = None
        self._public_key: ec.EllipticCurvePublicKey | None = None
        self._last_signature_size = 0

    def generate_keys(self) -> None:
        self._private_key = ec.generate_private_key(ec.SECP256K1())
        self._public_key = self._private_key.public_key()

    def _require_private(self) -> ec.EllipticCurvePrivateKey:
        if self._private_key is None:
            raise RuntimeError("wallet keys have not been generated")
        return self._private_key

    def sign(self, message: bytes) -> bytes:
        signature = self._require_private().sign(message, ec.ECDSA(hashes.SHA256()))
        self._last_signature_size = len(signature)
        return signature

    def verify(self, message: bytes, signature: bytes, public_key: bytes | None = None) -> bool:
        try:
            key = self._load_public_key(public_key)
            key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False

    def _load_public_key(self, public_key: bytes | None) -> ec.EllipticCurvePublicKey:
        if public_key is None:
            if self._public_key is None:
                raise ValueError("no public key available")
            return self._public_key
        try:
            return serialization.load_der_public_key(public_key)
        except ValueError:
            return ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), public_key)

    def get_public_key_bytes(self) -> bytes:
        if self._public_key is None:
            raise RuntimeError("wallet keys have not been generated")
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def get_algorithm_name(self) -> str:
        return ALGORITHM_ECDSA

    def get_signature_size(self) -> int:
        if self._last_signature_size:
            return self._last_signature_size
        return 70

    def get_public_key_size(self) -> int:
        return len(self.get_public_key_bytes())

    def export_secret_material(self) -> bytes:
        private = self._require_private()
        return private.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    @classmethod
    def from_secret_material(cls, material: bytes) -> ECDSAWallet:
        wallet = cls()
        wallet._private_key = serialization.load_der_private_key(material, password=None)
        wallet._public_key = wallet._private_key.public_key()
        return wallet
