"""Abstract wallet interface. Private keys must never be exposed."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseWallet(ABC):
    @abstractmethod
    def generate_keys(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def sign(self, message: bytes) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def verify(self, message: bytes, signature: bytes, public_key: bytes | None = None) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_public_key_bytes(self) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def get_algorithm_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_signature_size(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_public_key_size(self) -> int:
        raise NotImplementedError

    def export_secret_material(self) -> bytes:
        """Used only for encrypted wallet storage. Never print this value."""
        raise NotImplementedError
