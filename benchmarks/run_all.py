"""Collect metadata, write CSV/summary, and generate plots from real measurements."""

from __future__ import annotations

import csv
import json
import platform
import sys
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from benchmarks.benchmark_blockchain import run_storage_benchmarks
from benchmarks.benchmark_crypto import run_crypto_benchmarks
from benchmarks.plot_results import generate_all_plots
from config import (
    BENCHMARK_CSV,
    BENCHMARK_METADATA,
    BENCHMARK_SUMMARY,
    CRYPTO_BENCHMARK_ITERATIONS,
    MLDSA_VARIANT,
    REPORTS_DIR,
)


CSV_FIELDS = [
    "algorithm",
    "operation",
    "iterations",
    "average_time_ms",
    "min_time_ms",
    "max_time_ms",
    "std_dev_ms",
    "data_size_bytes",
    "serialized_transaction_size_avg",
    "public_key_size",
    "signature_size",
    "serialized_block_size",
    "total_blockchain_size",
    "transaction_count",
]


def _pkg_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unavailable"


def collect_metadata() -> dict:
    liboqs_version = "unavailable"
    try:
        import oqs

        if hasattr(oqs, "oqs_version"):
            liboqs_version = str(oqs.oqs_version())
        else:
            liboqs_version = getattr(oqs, "__version__", "unknown")
    except Exception as exc:
        liboqs_version = f"unavailable ({type(exc).__name__})"
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "python_version": sys.version,
        "operating_system": f"{platform.system()} {platform.release()} {platform.machine()}",
        "cryptography_version": _pkg_version("cryptography"),
        "liboqs_python_version": _pkg_version("liboqs-python"),
        "liboqs_version": liboqs_version,
        "ml_dsa_variant": MLDSA_VARIANT,
        "crypto_iterations": CRYPTO_BENCHMARK_ITERATIONS,
        "note": "Results are specific to this machine and environment.",
    }


def write_csv(rows: list[dict], path: Path = BENCHMARK_CSV) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def _lookup(rows: list[dict], algorithm: str, operation: str) -> dict | None:
    for row in rows:
        if row["algorithm"] == algorithm and row["operation"] == operation:
            return row
    return None


def write_summary(rows: list[dict], path: Path = BENCHMARK_SUMMARY) -> Path:
    ecdsa_sign = _lookup(rows, "ECDSA", "sign")
    mldsa_sign = _lookup(rows, "ML-DSA", "sign")
    ecdsa_sig = _lookup(rows, "ECDSA", "signature_size")
    mldsa_sig = _lookup(rows, "ML-DSA", "signature_size")
    lines = [
        "Benchmark summary for the educational quantum-resistant blockchain.",
        "These conclusions are based only on measurements collected in this experiment.",
        "",
    ]
    if ecdsa_sign and mldsa_sign:
        faster = "ECDSA" if ecdsa_sign["average_time_ms"] < mldsa_sign["average_time_ms"] else "ML-DSA"
        lines.append(
            f"On the tested environment, {faster} had lower average signing time "
            f"(ECDSA {ecdsa_sign['average_time_ms']:.4f} ms vs ML-DSA "
            f"{mldsa_sign['average_time_ms']:.4f} ms)."
        )
    if ecdsa_sig and mldsa_sig:
        lines.append(
            "ML-DSA provided post-quantum security properties but produced larger "
            f"signatures than ECDSA in this experiment "
            f"({int(mldsa_sig['data_size_bytes'])} bytes vs "
            f"{int(ecdsa_sig['data_size_bytes'])} bytes)."
        )
    lines.append(
        "Security properties and performance properties are distinct: a faster "
        "scheme is not automatically more secure."
    )
    lines.append(
        "Do not generalize one machine's timings to all platforms or all parameter sets."
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_all_benchmarks() -> dict:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    crypto_rows = run_crypto_benchmarks()
    storage_rows = run_storage_benchmarks()
    rows = crypto_rows + storage_rows
    csv_path = write_csv(rows)
    metadata = collect_metadata()
    BENCHMARK_METADATA.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    summary = write_summary(rows)
    plots = generate_all_plots(csv_path)
    return {
        "csv": str(csv_path),
        "metadata": str(BENCHMARK_METADATA),
        "summary": str(summary),
        "plots": [str(p) for p in plots],
        "row_count": len(rows),
    }


if __name__ == "__main__":
    print(json.dumps(run_all_benchmarks(), indent=2))
