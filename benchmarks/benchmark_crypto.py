"""Real ECDSA vs ML-DSA timing and size measurements."""

from __future__ import annotations

import statistics
import time
from typing import Any, Callable

from config import (
    ALGORITHM_ECDSA,
    ALGORITHM_MLDSA,
    CRYPTO_BENCHMARK_ITERATIONS,
    CRYPTO_WARMUP_ITERATIONS,
)
from crypto.crypto_factory import CryptoFactory


MESSAGE = b"quantum-resistant-blockchain-benchmark-message"


def _stats(samples: list[float], size: int, algorithm: str, operation: str) -> dict[str, Any]:
    ms = [value * 1000.0 for value in samples]
    return {
        "algorithm": algorithm,
        "operation": operation,
        "iterations": len(ms),
        "average_time_ms": statistics.fmean(ms),
        "min_time_ms": min(ms),
        "max_time_ms": max(ms),
        "std_dev_ms": statistics.pstdev(ms) if len(ms) > 1 else 0.0,
        "data_size_bytes": size,
    }


def _time_call(fn: Callable[[], Any], iterations: int, warmup: int) -> tuple[list[float], Any]:
    last = None
    for _ in range(warmup):
        last = fn()
    samples = []
    for _ in range(iterations):
        start = time.perf_counter()
        last = fn()
        samples.append(time.perf_counter() - start)
    return samples, last


def benchmark_algorithm(algorithm: str, iterations: int | None = None) -> list[dict[str, Any]]:
    rounds = iterations or CRYPTO_BENCHMARK_ITERATIONS
    results: list[dict[str, Any]] = []

    def generate():
        return CryptoFactory.create_wallet(algorithm)

    gen_samples, wallet = _time_call(generate, rounds, CRYPTO_WARMUP_ITERATIONS)
    results.append(_stats(gen_samples, wallet.get_public_key_size(), algorithm, "key_generation"))

    def sign():
        return wallet.sign(MESSAGE)

    sign_samples, signature = _time_call(sign, rounds, CRYPTO_WARMUP_ITERATIONS)
    results.append(_stats(sign_samples, len(signature), algorithm, "sign"))

    public_key = wallet.get_public_key_bytes()
    verifier = CryptoFactory.create_verifier(algorithm)

    def verify():
        return verifier.verify(MESSAGE, signature, public_key)

    verify_samples, _ = _time_call(verify, rounds, CRYPTO_WARMUP_ITERATIONS)
    results.append(_stats(verify_samples, len(public_key), algorithm, "verify"))
    results.append(
        {
            "algorithm": algorithm,
            "operation": "public_key_size",
            "iterations": 1,
            "average_time_ms": 0.0,
            "min_time_ms": 0.0,
            "max_time_ms": 0.0,
            "std_dev_ms": 0.0,
            "data_size_bytes": len(public_key),
        }
    )
    results.append(
        {
            "algorithm": algorithm,
            "operation": "signature_size",
            "iterations": 1,
            "average_time_ms": 0.0,
            "min_time_ms": 0.0,
            "max_time_ms": 0.0,
            "std_dev_ms": 0.0,
            "data_size_bytes": len(signature),
        }
    )
    return results


def run_crypto_benchmarks(iterations: int | None = None) -> list[dict[str, Any]]:
    rows = []
    for algorithm in (ALGORITHM_ECDSA, ALGORITHM_MLDSA):
        rows.extend(benchmark_algorithm(algorithm, iterations=iterations))
    return rows
